# タスクリスト

## 進捗
- 完了: 9 / 9 タスク

---

## タスク

- [x] 1. requirements.txt と Dockerfile を更新する
  - 対象: `requirements.txt`, `Dockerfile`
  - 内容:
    - `requirements.txt`: `pyvis`, `scikit-learn` を削除し `wordcloud==1.9.4` を追加
    - `Dockerfile`: `pip install` の前に `RUN apt-get update && apt-get install -y fonts-noto-cjk && rm -rf /var/lib/apt/lists/*` を追加

- [x] 2. `src/models.py` を更新する
  - 対象: `src/models.py`
  - 内容:
    - `Article` に `liked_count: int`, `publication_name: str | None`, `emoji: str` を追加
    - `ArticleContent` と `AnalysisResult` dataclass を削除（不要）

- [x] 3. `src/zenn_client.py` を更新する
  - 対象: `src/zenn_client.py`
  - 内容:
    - `get_all_articles()`: `liked_count`, `emoji`, `publication_name`（`item.get("publication") or {}` の `"name"` キー）を取得して `Article` にセット
    - `get_article_html()` と `fetch_body_texts()` は削除（本文取得なし）

- [x] 4. 不要なソースファイルを削除する
  - 対象: `src/knowledge_map.py`, `src/content_parser.py`, `src/phrase_analyzer.py`, `src/fortune_analyzer.py`
  - 内容: 4ファイルをすべて削除する

- [x] 5. `src/character_diagnosis.py` を新規作成する（トレイトスコアリング + くま名生成）
  - 対象: `src/character_diagnosis.py`（新規）
  - 内容:
    - `DiagnosisResult` dataclass を定義（`bear_name`, `top_traits: list[str]`, `trait_scores: dict[str, float]`, `bear_svg: str`）
    - `TRAIT_LABELS` / `TRAIT_ADJS` / `TRAIT_COLORS` dict を定義（design.md の表の通り）
    - `CharacterDiagnosis._score_traits(articles)`: 16トレイトをスコアリング（0-1）
      - `ai`: タイトル+タグに AI/LLM/ChatGPT/Claude/copilot/codex/antigravityを含む記事の割合
      - `infra`: タグに AWS/GCP/Azure/Docker/Kubernetes/Linux/Terraform を含む記事の割合
      - `backend`: タグに Python/Go/Java/Ruby/Rust/PHP/MySQL/PostgreSQL/DB/Database を含む記事の割合
      - `frontend`: タグに React/Vue/Next/Angular/TypeScript/CSS/HTML を含む記事の割合
      - `december`: 12月投稿記事の割合
      - `prolific`: `min(len(articles) / 30, 1.0)`
      - `sleepy`: 最終投稿から1年以上 or 記事数<5 なら 1.0、else 0.0
      - `fresh`: タイトルに「初心者」「入門」「初めて」「やってみた」を含む記事の割合
      - `event`: タイトルに「参加」「登壇」「LT」「イベント」「レポート」を含む記事の割合
      - `buzzy`: `min(max(liked_count per article) / 50, 1.0)`
      - `bookworm`: タイトルに「本」「書評」「読んだ」「まとめ」を含む記事の割合
      - `hackathon`: タイトルに「ハッカソン」「hackathon」を含むなら 0.8、else 0.0
      - `emoji_food`: `article.emoji` が食べ物絵文字（Unicodeコードポイント範囲で判定）の記事割合
          範囲: `(0x1F345, 0x1F37F)`, `(0x1F950, 0x1F96F)`, `(0x1F99E, 0x1F9C0)`, `(0x1FAD0, 0x1FADB)`
      - `emoji_cat`: `article.emoji` が猫絵文字（🐱🐈😺等）の記事割合（セット判定）
      - `emoji_bear`: `article.emoji` がくま絵文字（🐻🐼🧸🐻‍❄️）の記事割合（セット判定）
      - `casual`: タイトルに「してみた」「じゃん」「！」「？」「だよ」「だね」を含む記事の割合
    - `TRAIT_NAME_PARTS` dict を定義: key → くま名パーツ（例: `"ai": "ロボット"`, `"backend": "サラリー"` 等、spec.md のキャラ名から抽出）
    - `CharacterDiagnosis._make_bear_name(top3)`: `TRAIT_NAME_PARTS` を使って `"{p1}で、{p2}で、{p3}なくま"` を返す
    - `CharacterDiagnosis.diagnose(articles)`: スコア計算 → 上位3選出（全スコア<0.05なら`sleepy`強制1位）→ DiagnosisResult 返す

- [x] 6. `src/character_diagnosis.py` にくまSVG生成を追加する
  - 対象: `src/character_diagnosis.py`
  - 内容:
    - `BEAR_PIXELS: list[list[int]]` を 16×16 の2次元リストとして定数定義
      - `0` = 透明, `1` = ボディ色, `2` = 目・鼻（`#2D1B00`）, `3` = 口元（ボディ色を薄く）
    - アクセサリを16種類それぞれ SVG パーツ文字列として定義（`ACCESSORY_SVG: dict[str, str]`）
      - 各パーツは `<g>` タグでまとめ、ベアの座標系（160×160px）に合わせて配置
      - 例: `"buzzy"` → `<polygon points="60,10 80,30 100,10 ..." fill="#FFD700"/>` (王冠)
      - 例: `"ai"` → `<line x1="80" y1="10" x2="80" y2="30" stroke="#4A90D9" stroke-width="3"/><circle cx="80" cy="8" r="5" fill="#4A90D9"/>` (アンテナ)
    - `_make_bear_svg(top3_traits)` を実装:
      1. `BEAR_PIXELS` でボディを描画（色 = `TRAIT_COLORS[top3_traits[0]]`）
      2. `ACCESSORY_SVG[top3_traits[0]]` を重ねる（最も目立つ）
      3. `ACCESSORY_SVG[top3_traits[1]]` を重ねる（やや小さめに `transform="scale(0.8)"` 等）
      4. `ACCESSORY_SVG[top3_traits[2]]` を重ねる（控えめに `transform="scale(0.6)"` 等）
      5. `<svg>` タグでラップして返す

- [x] 7. `src/word_cloud_gen.py` を新規作成する
  - 対象: `src/word_cloud_gen.py`（新規）
  - 内容:
    - `NOTO_FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"` を定数定義
    - `WordCloudGen` クラス:
      - `__init__`: `nlp = spacy.load("ja_ginza", exclude=["compound_splitter"])` をロード
      - `generate(articles)`:
        1. 全タイトルを GiNZA で解析し NOUN/PROPN (len>=2) の単語リストを収集
        2. `wordcloud.WordCloud(font_path=NOTO_FONT_PATH, width=800, height=400, background_color="#FAF7F2", colormap="GnBu")` で生成
        3. `io.BytesIO` で PNG bytes として返す
        4. フォントファイルが存在しない場合は `font_path=None` にフォールバック

- [x] 8. `app.py` を全面書き直しする
  - 対象: `app.py`
  - 内容:
    - import: `CharacterDiagnosis`, `WordCloudGen`, `ZennClient` のみ（旧モジュール削除）
    - Lagoon CSS テーマ（既存スタイルを継承）
    - `run_analysis(username)`: `get_user` → `get_all_articles` → `fetch_body_texts`（プログレスバー表示） → `diagnose` → `word_cloud.generate` の結果をまとめて返す
    - 結果表示レイアウト:
      - 2カラム: 左=くまSVG（`st.components.v1.html`）、右=くま名（大きめ）+ トレイトバッジ3つ + ハートステータス
      - ハート: 通常記事=ターコイズ `♥`、publication記事=ゴールド `♥`（最大30個表示、超えたら `+N`）
      - 下部全幅: ワードクラウド（`st.image`）

- [x] 9. Docker ビルドして動作確認する
  - 対象: Docker 環境
  - 内容:
    - `docker compose up --build -d` を実行
    - `http://localhost:8501` でアプリが起動することを確認
    - Zenn ユーザー名（例: `michan74`）を入力し、くまキャラクターとワードクラウドが表示されることを確認
