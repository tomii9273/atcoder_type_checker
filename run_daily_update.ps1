[CmdletBinding()]
param(
    [string]$VirtualEnvironmentName = ".venv_dev",
    [string]$AtCoderCookieBrowser = "firefox",
    [string]$AtCoderCookieProfile = "Default",
    [switch]$Backfill
)

. (Join-Path $PSScriptRoot "run_update_common.ps1")

$repoPath = $PSScriptRoot
$appPath = Join-Path $repoPath "app"
$pythonPath = Join-Path $repoPath "$VirtualEnvironmentName\Scripts\python.exe"
$scriptPath = Join-Path $appPath "get_standing_and_join.py"
$dateSitePath = Join-Path $appPath "data\update_dates\date_site.txt"
$dateRankDataPath = Join-Path $appPath "data\update_dates\date_rank_data.txt"
$logContext = New-UpdateLogContext -RepoPath $repoPath -LogPrefix "daily_update"
$pointsPath = Join-Path $appPath "data\points\points.txt"

try {
    if (-not (Test-Path -LiteralPath $pythonPath)) {
        throw "Python が見つかりません: $pythonPath"
    }
    if (-not (Test-Path -LiteralPath $scriptPath)) {
        throw "実行対象の Python スクリプトが見つかりません: $scriptPath"
    }

    $env:ATCODER_COOKIE_BROWSER = $AtCoderCookieBrowser
    $env:ATCODER_COOKIE_PROFILE = $AtCoderCookieProfile
    $env:PYTHONUTF8 = "1"
    $env:PYTHONUNBUFFERED = "1"

    Write-UpdateLog -LogContext $logContext -Message "daily_update の実行を開始します。"
    Write-UpdateLog -LogContext $logContext -Message "ATCODER_COOKIE_BROWSER: $AtCoderCookieBrowser"
    Write-UpdateLog -LogContext $logContext -Message "ATCODER_COOKIE_PROFILE: $AtCoderCookieProfile"

    $pointsHashBefore = (Get-FileHash -LiteralPath $pointsPath -Algorithm SHA256).Hash
    $argumentList = @("-u", "`"$scriptPath`"")
    if ($Backfill) {
        $argumentList += "--backfill"
    }
    $pythonArguments = $argumentList -join " "
    $exitCode = Invoke-LoggedProcess `
        -LogContext $logContext `
        -FilePath $pythonPath `
        -Arguments $pythonArguments `
        -WorkingDirectory $appPath

    if ($exitCode -ne 0) {
        throw "Python スクリプトが異常終了しました。終了コード: $exitCode"
    }

    $pointsHashAfter = (Get-FileHash -LiteralPath $pointsPath -Algorithm SHA256).Hash
    if ($pointsHashBefore -eq $pointsHashAfter) {
        Write-UpdateLog -LogContext $logContext -Message "points.txt に変更がないため、更新日は変更しません。"
        return
    }

    $now = Get-JapanNow
    $yesterday = $now.AddDays(-1)
    Write-Utf8TextFile -Path $dateSitePath -Text ("{0}`n" -f (Get-DateText -DateTime $now))
    Write-Utf8TextFile -Path $dateRankDataPath -Text ("{0}`n" -f (Get-DateText -DateTime $yesterday))
    Write-UpdateLog -LogContext $logContext -Message "更新日ファイルを更新しました。"
    Write-UpdateLog -LogContext $logContext -Message "daily_update のローカルデータ更新が完了しました。"
}
catch {
    Write-UpdateLog -LogContext $logContext -Message "実行失敗: $($_.Exception.Message)"
    throw
}
finally {
    Remove-Item Env:ATCODER_COOKIE_BROWSER -ErrorAction SilentlyContinue
    Remove-Item Env:ATCODER_COOKIE_PROFILE -ErrorAction SilentlyContinue
    Remove-Item Env:PYTHONUTF8 -ErrorAction SilentlyContinue
    Remove-Item Env:PYTHONUNBUFFERED -ErrorAction SilentlyContinue
}
