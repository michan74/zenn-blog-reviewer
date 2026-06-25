# zennブログ分析

## 機能

- ユーザー毎にzenn記事を取得し、勝手にデータ分析する

### 分析内容

- 口癖の発見
- よく使う構文の発見
- 面白フレーズの発見
- スタンプの雰囲気で占い
- 記事内容をビジュアル化


## Zenn API

### ユーザー情報取得
- https://zenn.dev/api/users/michan74

### 記事一覧取得
- https://zenn.dev/api/articles?username=michan74&order=latest&page=1
- ※ Zenn APIは1ページあたり最大48件なので、ループし、取得

### 記事内容取得

- curl https://zenn.dev/michan74/articles/a88e616170c87e
  - URLをcurlすると、HTMLで取得できる。

