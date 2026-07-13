from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .models import Article


FOOD_EMOJI_RANGES = [
    (0x1F345, 0x1F37F),
    (0x1F950, 0x1F96F),
    (0x1F99E, 0x1F9C0),
    (0x1FAD0, 0x1FADB),
]

CAT_EMOJIS = {"🐱", "🐈", "😺", "🐈‍⬛", "😹", "😻", "🙀", "😿", "😼", "😽", "😾"}
BEAR_EMOJIS = {"🐻", "🐼", "🧸", "🐻‍❄️"}
DOG_EMOJIS = {"🐶", "🐕", "🐩", "🦮", "🐕‍🦺", "🐾"}

TRAIT_LABELS: dict[str, str] = {
    "ai":        "AI派",
    "infra":     "インフラ職人",
    "backend":   "バックエンド侍",
    "frontend":  "フロント職人",
    "december":  "師走の申し子",
    "prolific":  "量産型",
    "sleepy":    "冬眠中",
    "fresh":     "フレッシュ",
    "event":     "外面派",
    "buzzy":     "バズり屋",
    "bookworm":  "本の虫",
    "hackathon": "ハッカソン廃人",
    "emoji_food": "食いしん坊",
    "emoji_cat":  "ねこ派",
    "emoji_dog":  "犬派",
    "emoji_bear": "本物のくま",
    "casual":    "タメ口系",
    "poemer":    "ポエマー",
}

TRAIT_NAME_PARTS: dict[str, str] = {
    "december":   "メリクリ",
    "prolific":   "筋肉",
    "ai":         "ロボット",
    "casual":     "沼",
    "sleepy":     "眠り",
    "fresh":      "フレッシュ",
    "emoji_food": "食いしん坊",
    "event":      "外面いい",
    "buzzy":      "バズり",
    "emoji_cat":  "ねこ派",
    "emoji_dog":  "犬派",
    "hackathon":  "ひま",
    "emoji_bear": "正真正銘",
    "infra":      "工事",
    "backend":    "サラリー",
    "frontend":   "ホール",
    "bookworm":   "読書家",
    "poemer":     "ポエマー",
}

TRAIT_COLORS: dict[str, str] = {
    "ai":         "#4A90D9",
    "infra":      "#E8855A",
    "backend":    "#4A7C59",
    "frontend":   "#7B61FF",
    "december":   "#CC3333",
    "prolific":   "#E8B84B",
    "sleepy":     "#999999",
    "fresh":      "#2EBFB3",
    "event":      "#D4A574",
    "buzzy":      "#FFD700",
    "bookworm":   "#8B4513",
    "hackathon":  "#FF6B6B",
    "emoji_food": "#FF8C00",
    "emoji_cat":  "#F4A460",
    "emoji_dog":  "#DAA520",
    "emoji_bear": "#8B4513",
    "casual":     "#708090",
    "poemer":     "#9B59B6",
}

TRAIT_PRIORITY: dict[str, float] = {
    "ai":         1.0,
    "infra":      1.0,
    "backend":    1.0,
    "frontend":   1.0,
    "december":   0.8,
    "prolific":   0.65,
    "sleepy":     1.0,
    "fresh":      0.6,
    "event":      0.8,
    "buzzy":      0.7,
    "bookworm":   1.0,
    "hackathon":  0.8,
    "emoji_food": 1.0,
    "emoji_cat":  1.0,
    "emoji_dog":  1.0,
    "emoji_bear": 1.0,
    "casual":     0.5,
    "poemer":     1.0,
}

# 0=透明, 1=ボディ色, 2=目・鼻(ダーク), 3=口元(ライト)
BEAR_PIXELS: list[list[int]] = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # row 0
    [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0],  # row 1 - 耳
    [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0],  # row 2 - 耳
    [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],  # row 3 - 頭上
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],  # row 4 - 頭
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],  # row 5 - 頭(広)
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],  # row 6 - 頭(広)
    [0, 1, 1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 1, 1, 1, 0],  # row 7 - 目
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],  # row 8 - 顔
    [0, 1, 1, 1, 1, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 0],  # row 9 - 口元
    [0, 1, 1, 1, 1, 3, 2, 3, 3, 3, 3, 1, 1, 1, 1, 0],  # row 10 - 鼻
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],  # row 11 - あご
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],  # row 12 - 首
    [0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0],  # row 13 - 腕+胴
    [0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0],  # row 14 - 腕+胴
    [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],  # row 15 - 足
]

ACCESSORY_SVG: dict[str, str] = {
    "ai": (
        '<g>'
        '<line x1="80" y1="0" x2="80" y2="28" stroke="#4A90D9" stroke-width="3"/>'
        '<circle cx="80" cy="0" r="7" fill="#4A90D9"/>'
        '<circle cx="80" cy="0" r="3" fill="#FFFFFF"/>'
        '</g>'
    ),
    "infra": (
        '<g>'
        '<ellipse cx="80" cy="52" rx="48" ry="10" fill="#E8855A"/>'
        '<rect x="58" y="34" width="44" height="20" rx="4" fill="#E8855A"/>'
        '<rect x="68" y="28" width="24" height="10" rx="2" fill="#CC6633"/>'
        '</g>'
    ),
    "backend": (
        '<g>'
        '<polygon points="70,152 90,152 84,178 76,178" fill="#1A5F7A"/>'
        '<rect x="72" y="150" width="16" height="5" fill="#2EBFB3"/>'
        '</g>'
    ),
    "frontend": (
        '<g>'
        '<polygon points="80,5 42,52 118,52" fill="#7B61FF"/>'
        '<rect x="35" y="49" width="90" height="7" rx="3" fill="#FFFFFF"/>'
        '<rect x="42" y="44" width="76" height="6" rx="2" fill="#B8A0FF"/>'
        '</g>'
    ),
    "december": (
        '<g>'
        '<polygon points="80,5 42,57 118,57" fill="#CC3333"/>'
        '<rect x="35" y="54" width="90" height="9" rx="4" fill="#FFFFFF"/>'
        '<circle cx="80" cy="5" r="5" fill="#FFFFFF"/>'
        '</g>'
    ),
    "prolific": (
        '<g>'
        '<ellipse cx="20" cy="157" rx="16" ry="11" fill="#E8B84B"/>'
        '<ellipse cx="140" cy="157" rx="16" ry="11" fill="#E8B84B"/>'
        '</g>'
    ),
    "sleepy": (
        '<g>'
        '<text x="105" y="35" font-family="monospace" font-size="20" font-weight="bold" fill="#999999">Z</text>'
        '<text x="122" y="22" font-family="monospace" font-size="14" fill="#BBBBBB">z</text>'
        '<text x="134" y="13" font-family="monospace" font-size="10" fill="#DDDDDD">z</text>'
        '</g>'
    ),
    "fresh": (
        '<g>'
        '<rect x="45" y="40" width="70" height="10" rx="2" fill="#2D1B00"/>'
        '<rect x="52" y="26" width="56" height="16" rx="2" fill="#2EBFB3"/>'
        '<line x1="115" y1="40" x2="124" y2="28" stroke="#2D1B00" stroke-width="3"/>'
        '<circle cx="126" cy="26" r="5" fill="#2D1B00"/>'
        '</g>'
    ),
    "event": (
        '<g>'
        '<rect x="62" y="148" width="36" height="24" rx="2" fill="#FFFFFF" stroke="#1A5F7A" stroke-width="2"/>'
        '<line x1="68" y1="157" x2="92" y2="157" stroke="#1A5F7A" stroke-width="1.5"/>'
        '<line x1="68" y1="163" x2="86" y2="163" stroke="#1A5F7A" stroke-width="1.5"/>'
        '</g>'
    ),
    "buzzy": (
        '<g>'
        '<polygon points="80,14 68,34 48,34 63,46 57,66 80,54 103,66 97,46 112,34 92,34"'
        ' fill="#FFD700" stroke="#E8B84B" stroke-width="1.5"/>'
        '</g>'
    ),
    "bookworm": (
        '<g>'
        '<circle cx="53" cy="90" r="11" fill="none" stroke="#2D1B00" stroke-width="3"/>'
        '<circle cx="107" cy="90" r="11" fill="none" stroke="#2D1B00" stroke-width="3"/>'
        '<line x1="64" y1="90" x2="96" y2="90" stroke="#2D1B00" stroke-width="3"/>'
        '<line x1="28" y1="90" x2="42" y2="90" stroke="#2D1B00" stroke-width="3"/>'
        '<line x1="118" y1="90" x2="132" y2="90" stroke="#2D1B00" stroke-width="3"/>'
        '</g>'
    ),
    "hackathon": (
        '<g>'
        '<rect x="22" y="72" width="116" height="14" rx="3" fill="#FF6B6B"/>'
        '<rect x="22" y="72" width="24" height="14" rx="2" fill="#FFFFFF"/>'
        '<text x="50" y="83" font-family="sans-serif" font-size="9" fill="#FFFFFF">HACK</text>'
        '</g>'
    ),
    "emoji_food": (
        '<g>'
        '<path d="M52,148 Q80,140 108,148 L110,182 Q80,190 50,182 Z" fill="#FFFFFF" stroke="#DDD" stroke-width="2"/>'
        '<path d="M52,148 Q80,140 108,148 L108,157 Q80,149 52,157 Z" fill="#2EBFB3"/>'
        '</g>'
    ),
    "emoji_cat": (
        '<g>'
        '<polygon points="28,50 22,28 42,40" fill="#F4A460"/>'
        '<polygon points="132,50 138,28 118,40" fill="#F4A460"/>'
        '<polygon points="29,47 24,32 39,41" fill="#FFB6C1"/>'
        '<polygon points="131,47 136,32 121,41" fill="#FFB6C1"/>'
        '</g>'
    ),
    "emoji_dog": (
        '<g>'
        '<rect x="5" y="44" width="22" height="62" rx="11" fill="#DAA520"/>'
        '<rect x="133" y="44" width="22" height="62" rx="11" fill="#DAA520"/>'
        '</g>'
    ),
    "poemer": (
        '<g>'
        '<rect x="88" y="18" width="58" height="36" rx="8" fill="#9B59B6"/>'
        '<polygon points="96,54 108,54 100,66" fill="#9B59B6"/>'
        '<text x="94" y="42" font-family="sans-serif" font-size="20" fill="#FFFFFF">✦</text>'
        '</g>'
    ),
    "emoji_bear": (
        '<g>'
        '<polygon points="80,148 74,162 60,162 71,171 67,185 80,176 93,185 89,171 100,162 86,162"'
        ' fill="#FFD700"/>'
        '</g>'
    ),
    "casual": (
        '<g>'
        '<rect x="96" y="55" width="60" height="32" rx="6" fill="#FFFFFF" stroke="#2EBFB3" stroke-width="2"/>'
        '<polygon points="102,87 120,87 111,97" fill="#FFFFFF" stroke="#2EBFB3" stroke-width="2"/>'
        '<text x="101" y="76" font-family="sans-serif" font-size="11" fill="#1A5F7A">だよ！</text>'
        '</g>'
    ),
}

_AI_KEYWORDS = {"ai", "llm", "chatgpt", "claude", "copilot", "codex", "gemini", "機械学習", "深層学習", "生成ai"}
_INFRA_KEYWORDS = {"aws", "gcp", "azure", "docker", "kubernetes", "k8s", "linux", "terraform", "ansible"}
_BACKEND_KEYWORDS = {"python", "go", "java", "ruby", "rust", "php", "mysql", "postgresql", "django", "rails", "db", "database", "sql"}
_FRONTEND_KEYWORDS = {"react", "vue", "next.js", "next", "angular", "typescript", "css", "html", "svelte", "nuxt"}


@dataclass
class DiagnosisResult:
    bear_name: str
    top_traits: list[str]
    trait_scores: dict[str, float]
    bear_svg: str = ""


def _is_food_emoji(emoji: str) -> bool:
    if not emoji:
        return False
    cp = ord(emoji[0])
    return any(lo <= cp <= hi for lo, hi in FOOD_EMOJI_RANGES)


def _lighten_hex(hex_color: str, factor: float = 0.35) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return "#{:02X}{:02X}{:02X}".format(
        min(255, int(r + (255 - r) * factor)),
        min(255, int(g + (255 - g) * factor)),
        min(255, int(b + (255 - b) * factor)),
    )


class CharacterDiagnosis:
    def _score_traits(self, articles: list[Article]) -> dict[str, float]:
        n = len(articles)
        if n == 0:
            return {k: 0.0 for k in TRAIT_LABELS}

        scores: dict[str, float] = {}

        scores["ai"] = sum(
            1 for a in articles
            if any(kw in a.title.lower() for kw in _AI_KEYWORDS)
            or any(kw in t.lower() for kw in _AI_KEYWORDS for t in a.tags)
        ) / n

        scores["infra"] = sum(
            1 for a in articles
            if any(t.lower() in _INFRA_KEYWORDS for t in a.tags)
            or any(kw in a.title.lower() for kw in _INFRA_KEYWORDS)
        ) / n

        scores["backend"] = sum(
            1 for a in articles
            if any(t.lower() in _BACKEND_KEYWORDS for t in a.tags)
            or any(kw in a.title.lower() for kw in _BACKEND_KEYWORDS)
        ) / n

        scores["frontend"] = sum(
            1 for a in articles
            if any(t.lower() in _FRONTEND_KEYWORDS for t in a.tags)
            or any(kw in a.title.lower() for kw in _FRONTEND_KEYWORDS)
        ) / n

        scores["december"] = sum(
            1 for a in articles if a.published_at and a.published_at[5:7] == "12"
        ) / n

        scores["prolific"] = min(n / 50, 1.0)

        now = datetime.now(timezone.utc)
        last_pub = max((a.published_at for a in articles if a.published_at), default="")
        if n < 5:
            scores["sleepy"] = 1.0
        elif last_pub:
            try:
                last_dt = datetime.fromisoformat(last_pub)
                if last_dt.tzinfo is None:
                    last_dt = last_dt.replace(tzinfo=timezone.utc)
                scores["sleepy"] = 1.0 if (now - last_dt).days >= 365 else 0.0
            except ValueError:
                scores["sleepy"] = 0.0
        else:
            scores["sleepy"] = 0.0

        _fresh_kw = {"初心者", "入門", "初めて", "やってみた", "挑戦", "try"}
        scores["fresh"] = sum(1 for a in articles if any(kw in a.title for kw in _fresh_kw)) / n

        _event_kw = {"参加", "登壇", "LT", "イベント", "レポート"}
        scores["event"] = sum(1 for a in articles if any(kw in a.title for kw in _event_kw)) / n

        scores["buzzy"] = min(max((a.liked_count for a in articles), default=0) / 100, 1.0)

        _book_kw = {"書評", "読んだ", "読書","本", "図書"}
        scores["bookworm"] = sum(1 for a in articles if any(kw in a.title for kw in _book_kw)) / n

        hackathon_count = sum(
            1 for a in articles
            if "ハッカソン" in a.title or "hackathon" in a.title.lower()
        )
        scores["hackathon"] = min(hackathon_count / n * 4, 0.8)

        scores["emoji_food"] = sum(1 for a in articles if _is_food_emoji(a.emoji)) / n
        scores["emoji_cat"] = sum(1 for a in articles if a.emoji in CAT_EMOJIS) / n
        scores["emoji_dog"] = sum(1 for a in articles if a.emoji in DOG_EMOJIS) / n
        scores["emoji_bear"] = sum(1 for a in articles if a.emoji in BEAR_EMOJIS) / n

        _casual_kw = {"してみた", "じゃん", "だよ", "だね", "だよね", "〜","!","?","!?"}
        scores["casual"] = sum(1 for a in articles if any(kw in a.title for kw in _casual_kw)) / n

        scores["poemer"] = sum(1 for a in articles if a.article_type == "idea") / n

        return scores

    def _make_bear_name(self, top3: list[str]) -> str:
        parts = [TRAIT_NAME_PARTS[t] for t in top3]
        return f"{parts[0]}で、{parts[1]}で、{parts[2]}なくま"

    def _make_bear_svg(self, top3_traits: list[str]) -> str:
        body_color = TRAIT_COLORS[top3_traits[0]]
        muzzle_color = _lighten_hex(body_color)
        dark_color = "#2D1B00"

        pixel_size = 10
        y_offset = 20
        color_map = {1: body_color, 2: dark_color, 3: muzzle_color}

        rects = []
        for row_idx, row in enumerate(BEAR_PIXELS):
            for col_idx, pixel in enumerate(row):
                if pixel == 0:
                    continue
                x = col_idx * pixel_size
                y = row_idx * pixel_size + y_offset
                rects.append(f'<rect x="{x}" y="{y}" width="{pixel_size}" height="{pixel_size}" fill="{color_map[pixel]}"/>')

        opacities = [1.0, 0.7, 0.45]
        accessory_layers = []
        for i, trait in enumerate(top3_traits):
            acc = ACCESSORY_SVG.get(trait, "")
            if acc:
                accessory_layers.append(f'<g opacity="{opacities[i]}">{acc}</g>')

        return (
            '<svg xmlns="http://www.w3.org/2000/svg" width="160" height="200" viewBox="0 0 160 200">\n'
            + "\n".join(rects)
            + "\n"
            + "\n".join(accessory_layers)
            + "\n</svg>"
        )

    def diagnose(self, articles: list[Article]) -> DiagnosisResult:
        scores = self._score_traits(articles)
        sorted_traits = sorted(
            scores.items(),
            key=lambda x: x[1] * TRAIT_PRIORITY.get(x[0], 1.0),
            reverse=True,
        )

        if all(v < 0.05 for v in scores.values()):
            sorted_traits = [("sleepy", 1.0)] + [t for t in sorted_traits if t[0] != "sleepy"]

        top3 = [t for t, _ in sorted_traits[:3]]
        while len(top3) < 3:
            top3.append("sleepy")

        return DiagnosisResult(
            bear_name=self._make_bear_name(top3),
            top_traits=top3,
            trait_scores=scores,
            bear_svg=self._make_bear_svg(top3),
        )
