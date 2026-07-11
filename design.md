# 実装計画

## 方針・アーキテクチャ

Python + Streamlit の Web アプリ。ユーザー名 → Zenn API で全記事取得 → キャラクター診断 + ワードクラウド生成 → 結果表示。

- HTTP: `requests`
- HTML パース: `BeautifulSoup4`
- 形態素解析: `ja-ginza`（名詞抽出）
- ワードクラウド: `wordcloud` ライブラリ（Noto CJK フォント使用）
- くまSVG: Python 内でピクセルアート SVG 文字列を生成（外部ライブラリなし）
- UI: `streamlit`
- 開発環境: Docker

---

## ファイル構成

```
app.py                      — 変更: UIを全面書き直し（キャラ診断 + ワードクラウド表示）
src/
  models.py                 — 変更: Article に liked_count, publication_name を追加
  zenn_client.py            — 変更: liked_count/publication 取得、body text 抽出を追加
  character_diagnosis.py    — 新規: トレイトスコア計算 + くま名生成 + SVG生成
  word_cloud_gen.py         — 新規: タイトル名詞からワードクラウド画像生成
  knowledge_map.py          — 削除
  content_parser.py         — 削除
  phrase_analyzer.py        — 削除
  fortune_analyzer.py       — 削除
requirements.txt            — 変更: pyvis/scikit-learn削除、wordcloud追加
Dockerfile                  — 変更: fonts-noto-cjk インストール追加
```

---

## クラス・型定義

### Article（`src/models.py`）

```python
@dataclass
class Article:
    slug: str
    title: str
    published_at: str           # ISO8601 例: "2024-12-01T..."
    tags: list[str]
    liked_count: int            # 追加
    publication_name: str | None  # 追加: publication 経由なら名前、なければ None
    body_text: str = ""         # 追加: 本文テキスト（取得後にセット）
```

`User` / `AnalysisResult` は削除（不要になったため）。

---

### ZennClient（`src/zenn_client.py`）

- **主なメソッド**:
  - `get_user(username: str) -> User` — 変更なし
  - `get_all_articles(username: str) -> list[Article]` — 変更: `liked_count`, `publication_name` を取得
  - `fetch_body_texts(username: str, articles: list[Article]) -> None` — 追加: 全記事の本文HTMLを取得しパースして `article.body_text` にセット（sleep 0.5s/件）

`fetch_body_texts` は BeautifulSoup で `<article>` タグ内のテキストを抽出し `body_text` に代入する。

---

### CharacterDiagnosis（`src/character_diagnosis.py`）

- **役割**: 記事リストからトレイトを16種類スコアリングし、上位3つを組み合わせてくま名とSVGを生成する

#### トレイト一覧

| key | label（表示名） | スコア計算の根拠 |
|---|---|---|
| `ai` | AI派 | タイトル/タグに AI, LLM, ChatGPT, 機械学習 等 |
| `infra` | インフラ職人 | タグに AWS, GCP, Docker, Kubernetes, Linux 等 |
| `backend` | バックエンド侍 | タグに Python, Go, Java, Ruby, Rust, DB 等 |
| `frontend` | フロント職人 | タグに React, Vue, Next.js, CSS, TypeScript 等 |
| `december` | 師走の申し子 | 全記事のうち12月投稿の割合 |
| `prolific` | 量産型 | 総記事数（30件以上で最高スコア） |
| `sleepy` | 冬眠中 | 最終投稿から1年以上 or 記事数5件未満 |
| `fresh` | フレッシュ | タイトルに「初心者」「入門」「初めて」「やってみた」 |
| `event` | 外面派 | タイトルに「参加」「登壇」「LT」「イベント」「レポート」 |
| `buzzy` | バズり屋 | liked_count 合計が多い or 1記事で50以上 |
| `bookworm` | 本の虫 | タイトルに「本」「書評」「読んだ」「まとめ」 |
| `hackathon` | ハッカソン廃人 | タイトルに「ハッカソン」「hackathon」 |
| `emoji_food` | 食いしん坊 | body_text 中の食べ物絵文字（🍣🍜🍕等）の出現数 |
| `emoji_cat` | ねこ派 | body_text 中の猫絵文字（🐱🐈等）の出現数 |
| `emoji_bear` | 本物のくま | body_text 中のくま絵文字（🐻🐼等）の出現数 |
| `casual` | タメ口系 | body_text 中の「だよ」「だね」「じゃん」等の出現率 |

スコアは `0.0〜1.0` に正規化。全トレイト中スコアが低すぎる場合は `sleepy` を強制選出する。

#### くま名生成

上位3トレイトの名称パーツを連結して固定フォーマットで生成：

```
{part1}で、{part2}で、{part3}なくま
例: 「ロボットで、サラリーで、バズりなくま」
```

各トレイトのパーツは `TRAIT_NAME_PARTS` dict で定義（spec.md のキャラ名から抽出）：

```python
TRAIT_NAME_PARTS = {
    "december": "メリクリ",
    "prolific":  "筋肉",
    "ai":        "ロボット",
    "casual":    "沼",
    "sleepy":    "眠り",
    "fresh":     "フレッシュ",
    "emoji_food":"食いしん坊",
    "event":     "外面いい",
    "buzzy":     "バズり",
    "emoji_cat": "ねこ",
    "hackathon": "ひま",
    "emoji_bear":"正真正銘",
    "infra":     "工事",
    "backend":   "サラリー",
    "frontend":  "ホール",
    "bookworm":  "読書家",
}
```

#### くま SVG

16×16 ピクセルアートのくまを SVG の `<rect>` 要素で描画。ベアのボディは固定デザイン、上位3トレイトのアクセサリを重ねて個性を出す。

- キャンバス: `160×200px`（くま本体＋余白）
- ピクセルサイズ: 10×10px
- くまのボディ色: トップトレイトに対応するカラー（下記）
- アクセサリ: 上位3トレイトそれぞれのSVGパーツを重ねる（1位が最も目立つサイズ）

**各トレイトのアクセサリ**

| トレイト | アクセサリ |
|---|---|
| ai | アンテナ（頭上の細い棒＋先端の円） |
| infra | ヘルメット（頭を覆う半円） |
| backend | ネクタイ（胸元の三角形） |
| frontend | カラフルな帽子（三角帽） |
| december | サンタ帽（赤い帽子＋白いふち） |
| prolific | 筋肉アーム（両腕を太く） |
| sleepy | ZZZ テキスト（頭上） |
| fresh | 学士帽（四角い帽子） |
| event | 名刺（胸元の長方形） |
| buzzy | 王冠（頭上の三角ギザギザ） |
| bookworm | メガネ（目の上の2つの円） |
| hackathon | ハチマキ（頭の鉢巻き帯） |
| emoji_food | エプロン（胸元の台形） |
| emoji_cat | ネコ耳（耳の上に三角追加） |
| emoji_bear | 星マーク（胸元の★） |
| casual | 吹き出し「だよ！」（頭の横） |

| トレイト | くまカラー |
|---|---|
| ai | `#4A90D9`（ブルー） |
| infra | `#E8855A`（オレンジ） |
| backend | `#4A7C59`（グリーン） |
| frontend | `#7B61FF`（パープル） |
| december | `#CC3333`（レッド） |
| prolific | `#E8B84B`（ゴールド） |
| sleepy | `#999999`（グレー） |
| fresh | `#2EBFB3`（ターコイズ） |
| event | `#D4A574`（コーラル） |
| buzzy | `#FFD700`（ゴールド濃） |
| bookworm | `#8B4513`（ブラウン） |
| hackathon | `#FF6B6B`（ピンク） |
| emoji_food | `#FF8C00`（ダークオレンジ） |
| emoji_cat | `#F4A460`（サンディ） |
| emoji_bear | `#8B4513`（ブラウン） |
| casual | `#708090`（スレートグレー） |

くまのピクセル定義: `BEAR_PIXELS: list[list[int]]` として `character_diagnosis.py` 内に定数定義。`0` = 透明、`1` = くまボディ色、`2` = 目・鼻（ダーク）、`3` = 口元（ライト）。

- **メソッド**:
  - `diagnose(articles: list[Article]) -> DiagnosisResult` — トレイトスコア計算 → 上位3選出
  - `_score_traits(articles) -> dict[str, float]` — 全16トレイトをスコアリング
  - `_make_bear_name(top3: list[str]) -> str` — くま名文字列生成
  - `_make_bear_svg(top_trait: str) -> str` — SVG文字列生成

#### DiagnosisResult（dataclass）

```python
@dataclass
class DiagnosisResult:
    bear_name: str              # 例: "AI派で、フレッシュで、バズり屋なくま"
    top_traits: list[str]       # 上位3トレイトのkey
    trait_scores: dict[str, float]
    bear_svg: str               # SVG文字列
```

---

### WordCloudGen（`src/word_cloud_gen.py`）

- **役割**: 記事タイトルから名詞を抽出しワードクラウド画像を生成する
- **メソッド**:
  - `generate(articles: list[Article]) -> bytes` — PNG バイト列を返す（`st.image()` に渡す）
- **処理**:
  1. GiNZA で全タイトルから名詞を抽出
  2. `wordcloud.WordCloud(font_path=NOTO_FONT_PATH, ...)` で画像生成
  3. `io.BytesIO` で PNG バイト列として返す
- **フォントパス**: `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc`（Dockerfile でインストール）

---

## 主要な処理フロー

```
app.py: ユーザー名入力 → ボタン押下
  ZennClient.get_user()              → ユーザー情報
  ZennClient.get_all_articles()      → 記事一覧（liked_count、publication含む）
  ZennClient.fetch_body_texts()      → 全記事の本文テキスト取得（プログレスバーで表示）
  CharacterDiagnosis.diagnose()      → DiagnosisResult
  WordCloudGen.generate()            → PNG bytes

表示:
  ┌─────────────────────────────────────────────┐
  │ くまSVG          くま名                      │
  │                  トレイトバッジ x3            │
  │                  ハートステータス             │
  ├─────────────────────────────────────────────┤
  │ ワードクラウド（タイトルの頻出単語）           │
  └─────────────────────────────────────────────┘
```

### ステータス（ハート表示）

- 総記事数 → ハートの数（最大表示30個、超える場合は `+N` 表示）
- 通常記事: `♥`（ターコイズ）
- Publication 記事: `♥`（ゴールド）

---

## 考慮事項・決定事項

- **本文取得**: `fetch_body_texts` は 0.5s sleep。記事数が多い場合（>50件）は st.progress で進捗表示し体感を改善する
- **スコア正規化**: 各トレイトはカウントを最大期待値で割って `0-1` に clamp する。`sleepy` は他が全て 0 に近いとき強制上位に入る
- **くまSVG**: 外部ファイルなし、Python 文字列定数として管理。1種類のベアデザイン＋カラー変更で対応（アクセサリ追加は将来拡張）
- **ワードクラウド色**: Lagoon カラーパレット（ターコイズ系）に揃える
- **不要ファイル削除**: `knowledge_map.py`, `content_parser.py`, `phrase_analyzer.py`, `fortune_analyzer.py` は削除
- **キャッシュ**: `@st.cache_data` で同一ユーザーの再取得を抑制
- **Docker**: `FROM python:3.12-slim` + `apt-get install fonts-noto-cjk` で日本語フォント追加
