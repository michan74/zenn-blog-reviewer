# タスクリスト

## 進捗
- 完了: 1 / 12 タスク

---

## タスク

- [x] 1. Docker 開発環境のセットアップ
  - 対象: `Dockerfile`, `docker-compose.yml`, `requirements.txt`, `src/__init__.py`
  - 内容:
    - `requirements.txt` に `requests`, `beautifulsoup4`, `streamlit`, `pyvis` を記載
    - `Dockerfile` を作成（`python:3.12-slim` ベース、`COPY requirements.txt` → `pip install` → `CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]`）
    - `docker-compose.yml` を作成（ポート `8501:8501` マッピング、カレントディレクトリをボリュームマウントしてホットリロードを有効化）
    - `src/__init__.py` を作成してパッケージ化する
    - `docker compose up` でアプリが起動することを確認する

- [ ] 2. 共通データクラスの定義
  - 対象: `src/models.py`
  - 内容: `User`, `Article`, `ArticleContent`, `AnalysisResult` の dataclass を定義する。`AnalysisResult` には `knowledge_map_html: str` フィールドも含める

- [ ] 3. Zenn API クライアントの実装
  - 対象: `src/zenn_client.py`
  - 内容: `ZennClient` クラスを実装する
    - `get_user(username)` — `https://zenn.dev/api/users/{username}` を GET し `User` を返す。存在しない場合は例外を投げる
    - `get_all_articles(username)` — `https://zenn.dev/api/articles?username={username}&order=latest&page={n}` をページが空になるまでループし全 `Article` を返す
    - `get_article_html(username, slug)` — `https://zenn.dev/{username}/articles/{slug}` を GET し HTML 文字列を返す。`time.sleep(0.5)` を挟む

- [ ] 4. 記事HTMLパーサーの実装
  - 対象: `src/content_parser.py`
  - 内容: `ContentParser` クラスを実装する
    - `parse(html, slug, title)` — BeautifulSoup で記事本文テキストを抽出し、絵文字（unicodedata で判定）を別途リストに抽出して `ArticleContent` を返す

- [ ] 5. 口癖・構文パターン分析の実装
  - 対象: `src/phrase_analyzer.py`
  - 内容: `PhraseAnalyzer` クラスを実装する
    - `find_habits(texts)` — 「〜ですね」「〜かも」「〜ですが」「つまり」「要するに」「なるほど」等の正規表現パターンを `Counter` で集計し上位10件を返す
    - `find_syntax_patterns(texts)` — コードブロック数・見出し数・箇条書き数・リンク数を記事横断で集計し返す
    - `find_interesting_phrases(texts)` — 文中のユニークな表現（カタカナ語・比喩表現など）をランダムサンプリングして返す

- [ ] 6. 占いアナライザーの実装
  - 対象: `src/fortune_analyzer.py`
  - 内容: `FortuneAnalyzer` クラスを実装する
    - 絵文字をカテゴリ（ポジティブ系・テック系・食べ物系・自然系など）にマッピングするテーブルを定義
    - `analyze(emojis)` — 最頻出絵文字のカテゴリに対応する占いメッセージ `(絵文字, メッセージ)` を返す

- [ ] 7. 知識地図グラフの実装
  - 対象: `src/knowledge_map.py`
  - 内容: `KnowledgeMap` クラスを実装する
    - `build_graph(contents)` — 各 `ArticleContent` からキーワードを抽出（記事タイトルの単語 + 本文の英単語・カタカナ語、上位50件に絞る）し、同一記事内で共起した組み合わせにエッジを張る。ノードサイズ=出現頻度、エッジ太さ=共起回数で pyvis `Network` を構築し、Barnes-Hut 物理演算を有効にして HTML 文字列を返す

- [ ] 8. Streamlit UI の実装（基本レイアウト）
  - 対象: `app.py`
  - 内容: ユーザー名テキスト入力 + 「分析する」ボタンを配置。ボタン押下後に `st.spinner()` + `st.progress()` で記事取得の進捗を表示しながら全データを収集する。`@st.cache_data` で同一ユーザーの再取得をキャッシュする

- [ ] 9. 分析結果のタブ表示実装
  - 対象: `app.py`
  - 内容: `st.tabs()` で5タブを実装する
    - **あなたの知識地図**: `st.components.v1.html(knowledge_map_html, height=600)` で表示
    - **口癖**: 頻出フレーズを表・グラフで表示
    - **よく使う構文**: コードブロック・見出し等の使用回数を表示
    - **面白フレーズ**: `st.info()` や `st.markdown()` でランダム表示
    - **占い**: 絵文字と占いメッセージを大きく表示

- [ ] 11. エラーハンドリングの追加
  - 対象: `app.py`, `src/zenn_client.py`
  - 内容: 存在しないユーザー名・API エラー・ネットワークエラー時に `st.error()` でユーザーフレンドリーなメッセージを表示する

- [ ] 12. 動作確認・requirements.txt の最終調整
  - 対象: `requirements.txt`, `Dockerfile`
  - 内容: `docker compose up` で全機能を動作確認。バージョンを固定した `requirements.txt` を整備する。Streamlit Community Cloud へのデプロイ手順をメモ書きで `README.md` に記載する
