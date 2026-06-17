# Chrome Canary を拡張機能ロード状態で起動
# usage: .\launch_canary.ps1

$CanaryPath = "C:\Users\kayah\AppData\Local\Google\Chrome SxS\Application\chrome.exe"
$ExtensionPath = "C:\Users\kayah\Downloads\aa"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Chrome Canary Extension Launcher" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Canary が存在するか確認
if (-not (Test-Path $CanaryPath)) {
    Write-Host "Error: Chrome Canary not found at:" -ForegroundColor Red
    Write-Host "  $CanaryPath" -ForegroundColor Red
    Write-Host "`nInstall from: https://www.google.com/chrome/canary/" -ForegroundColor Yellow
    exit 1
}

Write-Host "Found Chrome Canary at: $CanaryPath`n" -ForegroundColor Green

Write-Host "Launching Chrome Canary with extension loaded..." -ForegroundColor Yellow
Write-Host "Command: $CanaryPath --load-extension=$ExtensionPath`n"

# Chrome Canary を起動
& $CanaryPath "--load-extension=$ExtensionPath" `
  --disable-background-networking `
  --disable-client-side-phishing-detection `
  --disable-sync `
  --no-first-run

Write-Host "`nChrome Canary launched" -ForegroundColor Green
