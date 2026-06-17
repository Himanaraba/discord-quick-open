# Discord Token Extractor - All Tests Runner
# 全テストを順番に実行

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Discord Token Extractor - Test Suite" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$testCount = 0
$passCount = 0

# Test 1: Static Structure Validation
Write-Host "[1/3] Running Static Structure Test..." -ForegroundColor Yellow
python test_extension.py
if ($LASTEXITCODE -eq 0) {
    $passCount++
}
$testCount++

Write-Host "`n"

# Test 2: Simulation Test (Recommended)
Write-Host "[2/3] Running Advanced Simulation Test (RECOMMENDED)..." -ForegroundColor Yellow
python test_simulation.py
if ($LASTEXITCODE -eq 0) {
    $passCount++
}
$testCount++

Write-Host "`n"

# Test 3: Browser Automation (Optional)
Write-Host "[3/3] Running Browser Automation Test (Optional - requires Chrome)..." -ForegroundColor Yellow
python test_browser.py
if ($LASTEXITCODE -eq 0) {
    $passCount++
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Test Suite Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Tests Passed: $passCount/$testCount" -ForegroundColor Green
Write-Host "Status: " -NoNewline

if ($passCount -eq $testCount) {
    Write-Host "ALL TESTS PASSED" -ForegroundColor Green
} else {
    Write-Host "SOME TESTS FAILED" -ForegroundColor Red
}

Write-Host ""
