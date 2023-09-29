# AtCoder Type Checker

AtCoder のコンテスト成績から「多く解くタイプ」であるか「早く解くタイプ」であるかを判定する Web アプリです。  
https://atcoder-type-checker.herokuapp.com/

## 関連リンク

- タスク一覧 (カンバン形式): https://github.com/tomii9273/atcoder_type_checker/projects/1
- Heroku 管理画面: https://dashboard.heroku.com/apps/atcoder-type-checker
- 作成者 Twitter: https://twitter.com/Tomii9273
- AtCoder: https://atcoder.jp
- 「#AtCoder_Type_Checker」での最新ツイート: https://twitter.com/search?q=%23AtCoder_Type_Checker%20&src=recent_search_click&f=live

## 仮想環境について (暫定・自分用)

venv を使用している。

- 本番環境 (`.venv_prod`): `requirements.txt`
  - このファイルは Heroku でデプロイ時に使われる。
- 開発環境 (`.venv_dev`): `requirements_dev.txt`
  - 本番環境のライブラリに加えて、分析用のものや linter が含まれる。

## スクリプト一覧

`app` ディレクトリに移動してから実行する。

- 現在のコードでアプリを表示する (デバッグ用): `python app.py`
- 補正値の更新: `python update_hoseichi.py -n name`
- 順位データの更新: `python get_standing_and_join.py`

## PR について (暫定・自分用)

- CI で「コミット時の日付 = サイト最終更新の日付 (`date_site.txt` のもの)」を確認している。そうでない場合、PR に「/date」とコメントすると GitHub Actions による日付更新コミットが行われる。
  - 「/date」からマージの間に日を跨がないよう注意
