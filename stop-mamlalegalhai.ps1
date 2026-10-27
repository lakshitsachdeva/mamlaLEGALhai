$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pidFile = Join-Path $projectRoot ".mamlalegalhai\server.pid"

if (-not (Test-Path $pidFile)) {
    Write-Host "No mamlaLEGALhai server PID was found."
    exit 0
}

$serverPid = Get-Content $pidFile
$process = Get-Process -Id $serverPid -ErrorAction SilentlyContinue
if ($process) {
    Stop-Process -Id $serverPid
    Write-Host "mamlaLEGALhai server stopped." -ForegroundColor Green
} else {
    Write-Host "mamlaLEGALhai was not running."
}
Remove-Item -LiteralPath $pidFile -Force
