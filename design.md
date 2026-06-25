# 実装計画

## 方針・アーキテクチャ

Python + Streamlit の Web アプリとして実装する。
ユーザー名を入力フォームで受け取り、Zenn API で全記事を取得→テキスト抽出→分析→画面表示 の流れで動く。
Streamlit Community Cloud に GitHub リポジトリを連携してデプロイする。

- HTTP リクエスト: `requests`
- HTML パース: `BeautifulSoup4`
- テキスト分析: 独自実装（`collections.Counter` + 正規表現）
- 知識地図: `pyvis`（force-directed graph）+ `streamlit-components`
- UI: `streamlit`

## ファイル構成

```
app.py                     — Streamlit エントリポイント: UI・全体オーケストレーション
src/
  zenn_client.py           — Zenn API クライアント（ユーザー情報・記事一覧・記事HTML取得）
  content_parser.py        — 記事HTMLからテキスト・絵文字を抽出
  phrase_analyzer.py       — 口癖・よく使う構文・面白フレーズの分析
  fortune_analyzer.py      — 絵文字の頻度から占いメッセージを生成
  knowledge_map.py         — キーワード共起グラフの構築・pyvis HTML生成
requirements.txt
Dockerfile                 — Python 3.12-slim ベース、streamlit run app.py を起動
docker-compose.yml         — ポート 8501 マッピング・ホットリロード用ボリューム設定
```

## クラス・型定義

### 共通データクラス (`src/models.py`)
```python
@dataclass
class User:
    username: str
    name: str

@dataclass
class Article:
    slug: str
    title: str
    published_at: str

@dataclass
class ArticleContent:
    slug: str
    title: str
    text: str
    emojis: list[str]

@dataclass
class AnalysisResult:
    username: str
    article_count: int
    habits: list[tuple[str, int]]          # (フレーズ, 出現回数)
    syntax_patterns: list[tuple[str, int]] # (パターン名, 出現回数)
    interesting_phrases: list[str]
    fortune: tuple[str, str]               # (絵文字, メッセージ)
    knowledge_map_html: str                # pyvis が生成した graph HTML
```

### ZennClient (`src/zenn_client.py`)
- **役割**: Zenn API へのHTTPリクエストをまとめる
- **主なメソッド**:
  - `get_user(username: str) -> User` — ユーザー情報取得
  - `get_all_articles(username: str) -> list[Article]` — 全記事取得（ページネーションループ）
  - `get_article_html(username: str, slug: str) -> str` — 記事HTMLを取得

### ContentParser (`src/content_parser.py`)
- **役割**: 記事HTMLからプレーンテキストと絵文字を抽出する
- **主なメソッド**:
  - `parse(html: str, slug: str, title: str) -> ArticleContent` — BeautifulSoup でテキスト・絵文字を取り出す

### PhraseAnalyzer (`src/phrase_analyzer.py`)
- **役割**: 複数記事のテキストを横断して頻出パターンを発見する
- **主なメソッド**:
  - `find_habits(texts: list[str]) -> list[tuple[str, int]]` — 口癖（文末表現・接続詞等）を集計
  - `find_syntax_patterns(texts: list[str]) -> list[tuple[str, int]]` — コードブロック・箇条書き等の構文頻度
  - `find_interesting_phrases(texts: list[str]) -> list[str]` — ユニークで面白い表現をサンプリング

### KnowledgeMap (`src/knowledge_map.py`)
- **役割**: 全記事のキーワードを抽出し、共起関係を pyvis の force-directed graph で可視化する
- **主なメソッド**:
  - `build_graph(contents: list[ArticleContent]) -> str` — 共起グラフを構築し、pyvis の HTML 文字列を返す
- **グラフの構造**:
  - ノード = 抽出キーワード（出現頻度が高いほどノードが大きい）
  - エッジ = 同一記事内で共起した関係（共起回数が多いほど線が太い）
  - レイアウト = pyvis の Barnes-Hut アルゴリズム（Obsidian に近い力学的配置）
- **Streamlit への埋め込み**: `st.components.v1.html(html, height=600)`

### FortuneAnalyzer (`src/fortune_analyzer.py`)
- **役割**: 絵文字の出現傾向から占いメッセージを生成する
- **主なメソッド**:
  - `analyze(emojis: list[str]) -> tuple[str, str]` — 最頻出絵文字に対応する占いメッセージを返す

## 主要な処理フロー

```
Streamlit UI (app.py)
  └─ テキスト入力: username
  └─ ボタン押下 → st.spinner() で処理中表示
       ZennClient.get_user()          → ユーザー存在確認・名前表示
       ZennClient.get_all_articles()  → 全記事取得（ページネーション）
       for each article:
         ZennClient.get_article_html() → HTML取得（sleep 0.5s）
         ContentParser.parse()          → テキスト・絵文字抽出
         st.progress() で進捗表示
       PhraseAnalyzer.find_habits()
       PhraseAnalyzer.find_syntax_patterns()
       PhraseAnalyzer.find_interesting_phrases()
       FortuneAnalyzer.analyze()
       KnowledgeMap.build_graph()
  └─ 結果を st.tabs() で分割表示
       - あなたの知識地図タブ（pyvis graph を st.components.v1.html で表示）
       - 口癖タブ
       - よく使う構文タブ
       - 面白フレーズタブ
       - 占いタブ
```

## 考慮事項・決定事項

- **レート制限対策**: 記事HTML取得は `time.sleep(0.5)` を挟む
- **キャッシュ**: `@st.cache_data` で同一ユーザーの再取得を抑制
- **口癖検出**: 「〜ですね」「〜かも」「つまり」「要するに」など文末・接続詞パターンを正規表現 + `Counter` で集計
- **構文パターン**: コードブロック(```)、見出し(#)、箇条書き(-) の使用頻度をカウント
- **占い**: 絵文字を感情カテゴリ（ポジティブ/テック系/食べ物など）にマッピングしメッセージを返す
- **開発環境**: Docker（`docker compose up` で起動、ホットリロードあり）
- **デプロイ**: Streamlit Community Cloud（GitHub 連携、無料）
- **知識地図のキーワード抽出**: 名詞・専門用語を正規表現で抽出（形態素解析なし）。記事タイトルの単語も優先的にノードに含める
- **ノード数の上限**: 多すぎると見づらいので上位50キーワードに絞る
