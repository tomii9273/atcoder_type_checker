# AtCoder Type Checker

[AtCoder](https://atcoder.jp) のコンテスト成績から「多く解くタイプ」であるか「早く解くタイプ」であるかを判定する Web アプリです。  
https://atcoder-type-checker.herokuapp.com/

## 関連リンク

- 作成者 X (Twitter): https://x.com/Tomii9273
- AtCoder: https://atcoder.jp
- 「#AtCoder_Type_Checker」での最新ポスト: https://x.com/search?q=%23AtCoder_Type_Checker%20&src=recent_search_click&f=live
- Heroku 管理画面 [Private]: https://dashboard.heroku.com/apps/atcoder-type-checker
- タスク一覧 (カンバン形式) [Private]: https://github.com/tomii9273/atcoder_type_checker/projects/1

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

## プルリクエストについて

- CI で「コミット時の日付 = サイト最終更新の日付 (`date_site.txt` のもの)」を確認しています。日付が異なる場合、PR に「/date」とコメントすると GitHub Actions による日付更新コミットが行われます。
  - main にマージする際、直前の CI が通っていない場合、または直前のコミットから日を跨いでいる場合は、「/date」を行ってからマージしてください。
- 機能・コードに大幅な変更を加える PR (例: 早解きの定義を変更する、全コードを Python でない言語で書き換える) は、マージしない場合があります。

## ライセンス

MIT License
