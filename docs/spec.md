# zennブログ分析

## 目的

- 自分の投稿の傾向を振り返る
  - 技術的なカテゴリー
  - 記事のカテゴリー
  - ワード



## 分析内容

### 投稿内容によるキャラクター診断

### ステータス
- 記事の数: ハートの数で表現
  - publicationの数: ハートの色を変える

### キャラクター診断

〇〇なクマというキャラクターに当てはめる

- 12月しか記事書かない人　 -> メリクリなくま
- 個人ブログたくさん書く人  -> 筋肉なくま
- AIについてたくさん書く人  -> ロボットなくま
- タメ口使う人 -> 沼なくま
- ここ１年以上記事書いていない、件数が少ない -> 眠りのくま
- 初心者/初めて/やってみた系の記事多い人 -> フレッシュなくま
- 食べ物の絵文字が多い人 -> 食いしん坊なくま
- イベント参加レポートが多い人 -> 外面いいくま
- いいね50以上の人 -> バズりなくま
- 絵文字に猫が多い人 -> ねこなくま
- AIハッカソンに参加している人  -> ひまくま
- くまの絵文字が多い人 -> 正真正銘のくま
- インフラ多い　-> 工事なくま
- バックエンド多い -> サラリーなくま
- フロントエンド多い -> ホールなくま
- 本読んだ系 -> 読書家のくま

### word cloud

- ワードクラウドを作成
  - タイトル
  - ブログ本文?(要調整)

## Zenn API

### ユーザー情報取得
- https://zenn.dev/api/users/michan74

### 記事一覧取得
- https://zenn.dev/api/articles?username=michan74&order=latest&page=1
- ※ Zenn APIは1ページあたり最大48件なので、ループし、取得

### 記事内容取得

- curl https://zenn.dev/michan74/articles/a88e616170c87e
  - URLをcurlすると、HTMLで取得できる。

## デザイン

- 絵文字、顔文字は利用しない

- たまごっち風　ドット絵

### 名前入力画面

- zennユーザー名の入力欄

### 分析結果画面

- 1ページで表示。
  - 知識地図
  - 口癖
  - 占い

### 色設定
- 色イメージ

Use case: ui-mockup
Asset type: Morphous light-mode design-system board
Primary request: Generate a comprehensive light-mode design-system board for Lagoon, derived from tropical lagoon shallows: turquoise clear water, white sand, palm shade, relaxed commerce system.
Canvas: wide 16:9 design board, 4K-class source, crisp UI mockup, large readable labels.
System identity: Lagoon; category landscape; context tropical coast; motif lagoon shallows; feel relaxed commerce system for browsing, product cards, checkout, dashboards, bookings, and inventory.
Visual language: airy white-sand surfaces, translucent turquoise panels, sea-glass accents, palm-shadow texture, shallow-water ripple dividers, calm commerce controls, precise grid, 8px component radius, soft coastal shadows.
Required visible sections: title "Lagoon", motif story, palette swatches named Turquoise Water, White Sand, Palm, Sea Glass, Coral Shell, Deep Channel; typography for English and Japanese UI; buttons, inputs, selects, textarea, checkbox, radio, switch, tabs, badges, alert, product card, price tag, cart summary, search command, navigation, dashboard metrics, table, chart, empty/error/loading states, spacing, radius, border, shadow, texture, token examples, generated asset examples.
Typography: readable multilingual product UI guidance with English and Japanese examples, short labels only.
Color constraints: use motif-derived turquoise water, white sand, palm green, shell neutrals, and deeper lagoon teal for contrast; avoid unrelated purple/blue gradients and saturated accent clutter.
Composition: premium shadcn/tweakcn-style product design system board, organized into clear full-width grid zones, not a landing page, no tiny dense token tables.
Text constraints: short readable UI labels, no random brand names, no watermark.

