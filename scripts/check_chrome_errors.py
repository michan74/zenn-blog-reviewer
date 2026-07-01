#!/usr/bin/env python3
"""
Chrome DevTools Protocol error checker for Claude Code PostToolUse hook.

Connects to Chrome running with --remote-debugging-port=9222,
waits for Streamlit to auto-reload after a file edit,
then reports any console errors back to Claude via asyncRewake.

Usage: Called automatically by Claude Code hook. Not intended for direct use.
"""

import json
import sys
import socket
import os
import struct
import time
import urllib.request
import re

CHROME_DEBUG_PORT = 9222
STREAMLIT_PORT = 8501
WAIT_SECONDS = 10  # リロード完了を待つ秒数

SKIP_EXTENSIONS = ('.md', '.txt', '.json', '.yaml', '.yml', '.toml', '.css')
NOISE_PATTERNS = ['favicon', 'AdBlock', 'extension://', 'chrome-extension']


def ws_connect(host, port, path):
    import base64
    sock = socket.create_connection((host, port), timeout=5)
    key = base64.b64encode(os.urandom(16)).decode()
    handshake = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        f"Sec-WebSocket-Version: 13\r\n\r\n"
    )
    sock.sendall(handshake.encode())
    buf = b""
    while b"\r\n\r\n" not in buf:
        chunk = sock.recv(1024)
        if not chunk:
            raise ConnectionError("Handshake failed")
        buf += chunk
    return sock


def ws_send(sock, data):
    payload = json.dumps(data).encode('utf-8')
    n = len(payload)
    mask = os.urandom(4)
    masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
    if n < 126:
        header = bytes([0x81, 0x80 | n]) + mask
    elif n < 65536:
        header = bytes([0x81, 0xFE]) + struct.pack('>H', n) + mask
    else:
        header = bytes([0x81, 0xFF]) + struct.pack('>Q', n) + mask
    sock.sendall(header + masked)


def ws_recv(sock):
    def read_exactly(n):
        buf = b""
        while len(buf) < n:
            chunk = sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("WebSocket closed")
            buf += chunk
        return buf

    header = read_exactly(2)
    opcode = header[0] & 0x0F
    masked = (header[1] & 0x80) != 0
    length = header[1] & 0x7F

    if length == 126:
        length = struct.unpack('>H', read_exactly(2))[0]
    elif length == 127:
        length = struct.unpack('>Q', read_exactly(8))[0]

    mask_key = read_exactly(4) if masked else b""
    data = read_exactly(length)
    if masked:
        data = bytes(b ^ mask_key[i % 4] for i, b in enumerate(data))

    if opcode == 8:  # close frame
        return None
    if opcode == 1:  # text frame
        return json.loads(data.decode('utf-8'))
    return {}  # ping/pong/binary


def is_noise(text):
    return any(n in text for n in NOISE_PATTERNS)


def main():
    try:
        hook_input = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    file_path = hook_input.get('tool_input', {}).get('file_path', '')
    if not file_path or file_path.endswith(SKIP_EXTENSIONS):
        sys.exit(0)

    # Chrome が起動しているか確認
    try:
        with urllib.request.urlopen(
            f'http://localhost:{CHROME_DEBUG_PORT}/json', timeout=3
        ) as r:
            tabs = json.loads(r.read())
    except Exception:
        sys.exit(0)  # Chrome未起動 → スキップ

    if not tabs:
        sys.exit(0)

    # StreamlitタブをURL優先で選択
    tab = next(
        (t for t in tabs if f':{STREAMLIT_PORT}' in t.get('url', '')),
        tabs[0]
    )

    ws_url = tab.get('webSocketDebuggerUrl', '')
    if not ws_url:
        sys.exit(0)

    m = re.match(r'ws://([^:/]+):(\d+)(/.+)', ws_url)
    if not m:
        sys.exit(0)

    host, port, path = m.group(1), int(m.group(2)), m.group(3)

    errors = []
    start = time.time()

    try:
        sock = ws_connect(host, port, path)
        sock.settimeout(1.0)

        # Console / Runtime / Log ドメインを有効化
        for cmd_id, method in enumerate(
            ['Console.enable', 'Runtime.enable', 'Log.enable'], start=1
        ):
            ws_send(sock, {'id': cmd_id, 'method': method, 'params': {}})

        # Streamlitのリロードを待ちながらエラー収集
        while time.time() - start < WAIT_SECONDS:
            try:
                msg = ws_recv(sock)
                if msg is None:
                    break

                method = msg.get('method', '')

                if method == 'Console.messageAdded':
                    m_data = msg['params']['message']
                    if m_data.get('level') == 'error':
                        text = m_data.get('text', '')
                        if text and not is_noise(text):
                            src = m_data.get('url', '')
                            line = m_data.get('line', '')
                            loc = f" ({src}:{line})" if src else ""
                            errors.append(f"[Console] {text}{loc}")

                elif method == 'Runtime.exceptionThrown':
                    exc = msg['params']['exceptionDetails']
                    desc = (
                        exc.get('exception', {}).get('description')
                        or exc.get('text', '')
                    )
                    if desc and not is_noise(desc):
                        errors.append(f"[Exception] {desc}")

                elif method == 'Log.entryAdded':
                    entry = msg['params']['entry']
                    if entry.get('level') == 'error':
                        text = entry.get('text', '')
                        if text and not is_noise(text):
                            errors.append(f"[Log] {text}")

            except socket.timeout:
                continue
            except Exception:
                break

        sock.close()

    except Exception:
        sys.exit(0)

    if not errors:
        sys.exit(0)

    # エラーをClaudeに通知 (asyncRewake: exit code 2)
    error_lines = "\n".join(f"  • {e}" for e in errors[:10])
    fname = os.path.basename(file_path)
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": (
                f"Chrome DevToolsでエラーが検出されました（{fname} 編集後）:\n"
                f"{error_lines}\n\n"
                "修正が必要か確認してください。"
            )
        }
    }
    print(json.dumps(output, ensure_ascii=False))
    sys.exit(2)


if __name__ == '__main__':
    main()
