[CmdletBinding()]
param(
    [string]$DailyStartTime = "15:00",
    [string]$MonthlyStartTime = "16:00"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)

function Register-UpdateTask {
    param(
        [Parameter(Mandatory = $true)]
        [string]$TaskName,
        [Parameter(Mandatory = $true)]
        [string]$Schedule,
        [Parameter(Mandatory = $true)]
        [string]$StartTime,
        [Parameter(Mandatory = $true)]
        [string]$ScriptPath,
        [string[]]$AdditionalArguments = @()
    )

    $taskCommand = 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{0}"' -f $ScriptPath
    $arguments = @(
        "/Create",
        "/SC",
        $Schedule,
        "/TN",
        $TaskName,
        "/TR",
        $taskCommand,
        "/ST",
        $StartTime,
        "/F"
    ) + $AdditionalArguments

    & schtasks.exe $arguments
    if ($LASTEXITCODE -ne 0) {
        throw "タスクの登録に失敗しました: $TaskName"
    }
}

$dailyScriptPath = Join-Path $PSScriptRoot "run_daily_update.ps1"
$monthlyScriptPath = Join-Path $PSScriptRoot "run_monthly_hoseichi_update.ps1"

Register-UpdateTask `
    -TaskName "AtCoderTypeCheckerDailyUpdate" `
    -Schedule "DAILY" `
    -StartTime $DailyStartTime `
    -ScriptPath $dailyScriptPath

Register-UpdateTask `
    -TaskName "AtCoderTypeCheckerMonthlyHoseichiUpdate" `
    -Schedule "MONTHLY" `
    -StartTime $MonthlyStartTime `
    -ScriptPath $monthlyScriptPath `
    -AdditionalArguments @("/D", "1")

Write-Host "日次・月次の更新タスクを登録しました。"
