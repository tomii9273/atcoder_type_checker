[CmdletBinding()]
param(
    [string]$VirtualEnvironmentName = ".venv_dev",
    [string]$AtCoderCookieBrowser = "firefox",
    [string]$AtCoderCookieProfile = "Default",
    [string]$FileName = "",
    [switch]$DebugRun
)

. (Join-Path $PSScriptRoot "run_update_common.ps1")

function Get-AvailableFileName {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DirectoryPath,
        [Parameter(Mandatory = $true)]
        [string]$BaseFileName
    )

    $candidate = $BaseFileName
    if (-not $candidate.EndsWith(".npy")) {
        $candidate += ".npy"
    }

    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($candidate)
    $extension = [System.IO.Path]::GetExtension($candidate)
    $index = 1
    while (Test-Path -LiteralPath (Join-Path $DirectoryPath $candidate)) {
        $candidate = "{0}_{1}{2}" -f $baseName, $index, $extension
        $index += 1
    }

    return $candidate
}

$repoPath = $PSScriptRoot
$appPath = Join-Path $repoPath "app"
$pythonPath = Join-Path $repoPath "$VirtualEnvironmentName\Scripts\python.exe"
$scriptPath = Join-Path $appPath "update_hoseichi.py"
$hoseichiDirectory = Join-Path $appPath "data\hoseichi"
$constPath = Join-Path $appPath "src\const.py"
$dateSitePath = Join-Path $appPath "data\update_dates\date_site.txt"
$dateHoseichiPath = Join-Path $appPath "data\update_dates\date_hoseichi.txt"
$logContext = New-UpdateLogContext -RepoPath $repoPath -LogPrefix "monthly_hoseichi_update"

try {
    if (-not (Test-Path -LiteralPath $pythonPath)) {
        throw "Python が見つかりません: $pythonPath"
    }
    if (-not (Test-Path -LiteralPath $scriptPath)) {
        throw "実行対象の Python スクリプトが見つかりません: $scriptPath"
    }
    if (-not (Test-Path -LiteralPath $constPath)) {
        throw "const.py が見つかりません: $constPath"
    }

    $now = Get-JapanNow
    $baseFileName = $FileName
    if ([string]::IsNullOrWhiteSpace($baseFileName)) {
        $filePrefix = if ($DebugRun) { "debug_5ntop" } else { "monthly_5ntop" }
        $baseFileName = "{0}_{1}" -f $filePrefix, $now.ToString("yyyyMMdd")
    }
    $resolvedFileName = Get-AvailableFileName -DirectoryPath $hoseichiDirectory -BaseFileName $baseFileName
    $relativeHoseichiPath = "data/hoseichi/{0}" -f $resolvedFileName.Replace("\", "/")
    $createdFilePath = Join-Path $hoseichiDirectory $resolvedFileName

    $env:ATCODER_COOKIE_BROWSER = $AtCoderCookieBrowser
    $env:ATCODER_COOKIE_PROFILE = $AtCoderCookieProfile
    $env:PYTHONUTF8 = "1"
    $env:PYTHONUNBUFFERED = "1"

    Write-UpdateLog -LogContext $logContext -Message "monthly_hoseichi_update の実行を開始します。"
    Write-UpdateLog -LogContext $logContext -Message "ATCODER_COOKIE_BROWSER: $AtCoderCookieBrowser"
    Write-UpdateLog -LogContext $logContext -Message "ATCODER_COOKIE_PROFILE: $AtCoderCookieProfile"
    Write-UpdateLog -LogContext $logContext -Message "出力ファイル名: $resolvedFileName"

    $argumentList = @(
        "-u",
        "`"$scriptPath`"",
        "-n",
        "`"$resolvedFileName`""
    )
    if ($DebugRun) {
        $argumentList += "-d"
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
    if (-not (Test-Path -LiteralPath $createdFilePath)) {
        throw "補正値ファイルが見つかりません: $createdFilePath"
    }

    if ($DebugRun) {
        Write-UpdateLog -LogContext $logContext -Message "デバッグ実行のため、const.py と更新日は変更しません。"
        return
    }

    $constText = [System.IO.File]::ReadAllText($constPath)
    $constPattern = '(?m)^HOSEICHI_FILE_PATH = ".*"$'
    if (-not [regex]::IsMatch($constText, $constPattern)) {
        throw "const.py に HOSEICHI_FILE_PATH が見つかりません。"
    }
    $newConstText = [regex]::Replace(
        $constText,
        $constPattern,
        ('HOSEICHI_FILE_PATH = "{0}"' -f $relativeHoseichiPath)
    )
    Write-Utf8TextFile -Path $constPath -Text $newConstText
    Write-Utf8TextFile -Path $dateSitePath -Text ("{0}`n" -f (Get-DateText -DateTime $now))
    Write-Utf8TextFile -Path $dateHoseichiPath -Text ("{0}`n" -f (Get-DateText -DateTime $now))
    Write-UpdateLog -LogContext $logContext -Message "const.py と更新日ファイルを更新しました。"

    Write-UpdateLog -LogContext $logContext -Message "monthly_hoseichi_update のローカルデータ更新が完了しました。"
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
