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

## ローカルでのデータ更新 (作成者用)

AtCoder のログイン仕様変更に伴い、順位データと補正値データは Windows PC 上の通常ブラウザの Cookie を使って取得する。GitHub Actions からは更新しない。

1. リポジトリ直下で開発用仮想環境を作成し、依存関係をインストールする。

   ```powershell
   python -m venv .venv_dev
   .\.venv_dev\Scripts\python.exe -m pip install -r requirements_dev.txt
   ```

2. Firefox で AtCoder にログインする。
3. 必要に応じて手動実行する。

   ```powershell
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\run_daily_update.ps1"
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\run_monthly_hoseichi_update.ps1"
   ```

   Firefox 以外を使う場合は、`-AtCoderCookieBrowser chrome` または `-AtCoderCookieBrowser edge` を指定する。通常プロファイル以外は `-AtCoderCookieProfile ProfileName` も指定する。Chrome・Edge は Cookie DB を読めない場合があるため、その場合はブラウザを閉じてから実行する。

   順位データに長期間の未更新や欠落がある場合は、`run_daily_update.ps1 -Backfill` を実行する。AtCoder のコンテストアーカイブを全ページ確認し、過去の未取得コンテストも補完する。

4. タスクスケジューラへ日次 (毎日 15:00)・月次 (毎月 1 日 16:00) の実行を登録する。

   ```powershell
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\register_update_tasks.ps1"
   ```

登録時刻を変える場合は `-DailyStartTime "14:00" -MonthlyStartTime "17:00"` のように指定する。同名タスクは再登録時に置き換わる。ブラウザプロファイルへアクセスするため、タスクは登録した Windows ユーザーで実行する。

ログは `ignore/logs` と `ignore/*_last.log` に保存される。`.ps1` はローカルのデータだけを更新し、コミット、push、`main` へのマージ、Heroku へのデプロイは行わない。

月次処理を少量のデータで確認する場合は、次を使う。デバッグ用 `.npy` だけを生成し、サイトで使う補正値や更新日は変更しない。

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\run_monthly_hoseichi_update.ps1" -DebugRun
```

## その他のスクリプト

`app` ディレクトリに移動してから実行する。

- 現在のコードでアプリを表示する (デバッグ用): `python app.py`

## プルリクエストについて

- CI で「コミット時の日付 = サイト最終更新の日付 (`date_site.txt` のもの)」を確認しています。日付が異なる場合、PR に「/date」とコメントすると GitHub Actions による日付更新コミットが行われます。
  - main にマージする際、直前の CI が通っていない場合、または直前のコミットから日を跨いでいる場合は、「/date」を行ってからマージしてください。
- 機能・コードに大幅な変更を加える PR (例: 早解きの定義を変更する、全コードを Python でない言語で書き換える) は、マージしない場合があります。

## ライセンス

MIT License
