$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pidFile = Join-Path $projectRoot ".regulatrace\server.pid"

if (-not (Test-Path $pidFile)) {
    Write-Host "No RegulaTrace server PID was found."
    exit 0
}

$serverPid = Get-Content $pidFile
$process = Get-Process -Id $serverPid -ErrorAction SilentlyContinue
if ($process) {
    Stop-Process -Id $serverPid
    Write-Host "RegulaTrace server stopped." -ForegroundColor Green
} else {
    Write-Host "RegulaTrace was not running."
}
Remove-Item -LiteralPath $pidFile -Force
