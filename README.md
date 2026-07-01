# Zenn ブログ分析

Zenn ユーザーの記事を分析して、口癖・よく使う構文・知識地図・絵文字占いを表示する Streamlit アプリです。

## ローカル開発（Docker）

```bash
docker compose up
```

http://localhost:8501 でアクセスできます。コードを変更するとホットリロードで即反映されます。

## Streamlit Community Cloud へのデプロイ

1. このリポジトリを GitHub に push する
2. [share.streamlit.io](https://share.streamlit.io) にアクセスしてログイン
3. "New app" → リポジトリ・ブランチ・`app.py` を選択
4. "Deploy" をクリック

> `requirements.txt` が存在すれば依存関係は自動でインストールされます。

## 技術スタック

| 用途 | ライブラリ |
|------|-----------|
| HTTP リクエスト | requests |
| HTML パース | BeautifulSoup4 |
| 知識地図グラフ | pyvis |
| UI | Streamlit |
