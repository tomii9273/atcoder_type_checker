# AtCoder Type Checker

AtCoder のコンテスト成績から「多く解くタイプ」であるか「早く解くタイプ」であるかを判定する Web アプリです。  
https://atcoder-type-checker.herokuapp.com/  

## 関連リンク

- タスク一覧 (カンバン形式): https://github.com/tomii9273/atcoder_type_checker/projects/1
- Heroku 管理画面: https://dashboard.heroku.com/apps/atcoder-type-checker
- 作成者 Twitter: https://twitter.com/Tomii9273
- AtCoder: https://atcoder.jp
- 「#AtCoder_Type_Checker」での最新ツイート: https://twitter.com/search?q=%23AtCoder_Type_Checker%20&src=recent_search_click&f=live

## PR について (暫定・自分用)

- CI で「コミット時の日付 = サイト最終更新の日付 (`date_site.txt` のもの)」を確認している。そうでない場合、PR に「/date」とコメントすると GitHub Action による日付更新コミットが行われる。
  - 「/date」からマージの間に日を跨がないよう注意
