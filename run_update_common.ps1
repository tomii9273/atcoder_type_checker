$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$script:Utf8Encoding = [System.Text.UTF8Encoding]::new($false)
$script:TokyoTimeZone = [System.TimeZoneInfo]::FindSystemTimeZoneById("Tokyo Standard Time")

function Initialize-Utf8LogFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    [System.IO.File]::WriteAllText($Path, "", $script:Utf8Encoding)
}

function New-UpdateLogContext {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoPath,
        [Parameter(Mandatory = $true)]
        [string]$LogPrefix
    )

    $logDirectory = Join-Path $RepoPath "ignore\logs"
    $latestLogPath = Join-Path $RepoPath "ignore\${LogPrefix}_last.log"
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $logPath = Join-Path $logDirectory "${LogPrefix}_$timestamp.log"

    New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
    Initialize-Utf8LogFile -Path $logPath
    Initialize-Utf8LogFile -Path $latestLogPath

    return @{
        LogPath = $logPath
        LatestLogPath = $latestLogPath
    }
}

function Write-UpdateOutputLine {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$LogContext,
        [Parameter(Mandatory = $true)]
        [AllowEmptyString()]
        [string]$Line
    )

    Write-Host $Line
    [System.IO.File]::AppendAllText(
        $LogContext.LogPath,
        "$Line`r`n",
        $script:Utf8Encoding
    )
    [System.IO.File]::AppendAllText(
        $LogContext.LatestLogPath,
        "$Line`r`n",
        $script:Utf8Encoding
    )
}

function Write-UpdateLog {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$LogContext,
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Write-UpdateOutputLine -LogContext $LogContext -Line $line
}

function Invoke-LoggedProcess {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$LogContext,
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [Parameter(Mandatory = $true)]
        [string]$Arguments,
        [Parameter(Mandatory = $true)]
        [string]$WorkingDirectory
    )

    $processStartInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processStartInfo.FileName = $FilePath
    $processStartInfo.Arguments = $Arguments
    $processStartInfo.WorkingDirectory = $WorkingDirectory
    $processStartInfo.UseShellExecute = $false
    $processStartInfo.CreateNoWindow = $true
    $processStartInfo.RedirectStandardOutput = $true
    $processStartInfo.RedirectStandardError = $true

    if ($processStartInfo.PSObject.Properties.Name -contains "StandardOutputEncoding") {
        $processStartInfo.StandardOutputEncoding = [System.Text.UTF8Encoding]::new($false)
    }
    if ($processStartInfo.PSObject.Properties.Name -contains "StandardErrorEncoding") {
        $processStartInfo.StandardErrorEncoding = [System.Text.UTF8Encoding]::new($false)
    }

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $processStartInfo
    [void]$process.Start()

    while (-not $process.HasExited) {
        while (-not $process.StandardOutput.EndOfStream) {
            Write-UpdateOutputLine -LogContext $LogContext -Line $process.StandardOutput.ReadLine()
        }
        while (-not $process.StandardError.EndOfStream) {
            Write-UpdateOutputLine -LogContext $LogContext -Line $process.StandardError.ReadLine()
        }
        Start-Sleep -Milliseconds 100
    }

    while (-not $process.StandardOutput.EndOfStream) {
        Write-UpdateOutputLine -LogContext $LogContext -Line $process.StandardOutput.ReadLine()
    }
    while (-not $process.StandardError.EndOfStream) {
        Write-UpdateOutputLine -LogContext $LogContext -Line $process.StandardError.ReadLine()
    }

    $process.WaitForExit()
    $exitCode = $process.ExitCode
    $process.Close()
    return $exitCode
}

function Write-Utf8TextFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [Parameter(Mandatory = $true)]
        [string]$Text
    )

    [System.IO.File]::WriteAllText($Path, $Text, $script:Utf8Encoding)
}

function Get-JapanNow {
    return [System.TimeZoneInfo]::ConvertTimeFromUtc(
        [DateTime]::UtcNow,
        $script:TokyoTimeZone
    )
}

function Get-DateText {
    param(
        [Parameter(Mandatory = $true)]
        [datetime]$DateTime
    )

    return $DateTime.ToString("yyyy-MM-dd")
}
