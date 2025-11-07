# Validation script to check all deliverables are present

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "UI/UX Improvement Evaluation - Deliverables Validation" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$workspaceRoot = $PSScriptRoot
$allGood = $true

function Test-File {
    param($path, $description)
    $fullPath = Join-Path $workspaceRoot $path
    if (Test-Path $fullPath) {
        Write-Host "✅ $description" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ MISSING: $description" -ForegroundColor Red
        Write-Host "   Expected at: $fullPath" -ForegroundColor Yellow
        return $false
    }
}

Write-Host "Checking Root Files..." -ForegroundColor Yellow
$allGood = (Test-File "test_data.json" "Canonical test data") -and $allGood
$allGood = (Test-File "compare_results.py" "Comparison tool") -and $allGood
$allGood = (Test-File "run_all.ps1" "Master execution script") -and $allGood
$allGood = (Test-File "README.md" "Main documentation") -and $allGood
$allGood = (Test-File "QUICKSTART.md" "Quick start guide") -and $allGood
$allGood = (Test-File "DELIVERABLES_SUMMARY.md" "Deliverables summary") -and $allGood

Write-Host ""
Write-Host "Checking Project A (Pre-Improvement)..." -ForegroundColor Yellow
$allGood = (Test-File "Project_A_PreImprove_UI\src\index.html" "Project A - HTML") -and $allGood
$allGood = (Test-File "Project_A_PreImprove_UI\src\styles.css" "Project A - CSS") -and $allGood
$allGood = (Test-File "Project_A_PreImprove_UI\src\modal.js" "Project A - JavaScript") -and $allGood
$allGood = (Test-File "Project_A_PreImprove_UI\server\server.py" "Project A - Server") -and $allGood
$allGood = (Test-File "Project_A_PreImprove_UI\data\sample_data.json" "Project A - Sample data") -and $allGood
$allGood = (Test-File "Project_A_PreImprove_UI\tests\test_pre_ui.py" "Project A - Test harness") -and $allGood
$allGood = (Test-File "Project_A_PreImprove_UI\requirements.txt" "Project A - Requirements") -and $allGood
$allGood = (Test-File "Project_A_PreImprove_UI\setup.sh" "Project A - Setup script") -and $allGood
$allGood = (Test-File "Project_A_PreImprove_UI\run_tests.ps1" "Project A - Test runner") -and $allGood
$allGood = (Test-File "Project_A_PreImprove_UI\README.md" "Project A - Documentation") -and $allGood

Write-Host ""
Write-Host "Checking Project B (Post-Improvement)..." -ForegroundColor Yellow
$allGood = (Test-File "Project_B_PostImprove_UI\src\index.html" "Project B - HTML") -and $allGood
$allGood = (Test-File "Project_B_PostImprove_UI\src\styles.improved.css" "Project B - CSS") -and $allGood
$allGood = (Test-File "Project_B_PostImprove_UI\src\wizard.js" "Project B - JavaScript") -and $allGood
$allGood = (Test-File "Project_B_PostImprove_UI\server\server.py" "Project B - Server") -and $allGood
$allGood = (Test-File "Project_B_PostImprove_UI\data\expected_post.json" "Project B - Expected results") -and $allGood
$allGood = (Test-File "Project_B_PostImprove_UI\tests\test_post_ui.py" "Project B - Test harness") -and $allGood
$allGood = (Test-File "Project_B_PostImprove_UI\requirements.txt" "Project B - Requirements") -and $allGood
$allGood = (Test-File "Project_B_PostImprove_UI\setup.sh" "Project B - Setup script") -and $allGood
$allGood = (Test-File "Project_B_PostImprove_UI\run_tests.ps1" "Project B - Test runner") -and $allGood
$allGood = (Test-File "Project_B_PostImprove_UI\README.md" "Project B - Documentation") -and $allGood

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan

if ($allGood) {
    Write-Host "✅ ALL DELIVERABLES PRESENT!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Ready to execute!" -ForegroundColor Green
    Write-Host "Run: .\run_all.ps1" -ForegroundColor Yellow
    Write-Host ""
    
    # Show summary
    Write-Host "Summary:" -ForegroundColor Cyan
    Write-Host "  📁 Root files: 6" -ForegroundColor White
    Write-Host "  📁 Project A files: 10" -ForegroundColor White
    Write-Host "  📁 Project B files: 10" -ForegroundColor White
    Write-Host "  📁 Total: 26 core files" -ForegroundColor White
    Write-Host ""
    Write-Host "Test Coverage:" -ForegroundColor Cyan
    Write-Host "  🧪 Test cases: 5" -ForegroundColor White
    Write-Host "  📊 Metrics tracked: 10+" -ForegroundColor White
    Write-Host "  📸 Screenshots: 20+" -ForegroundColor White
    Write-Host ""
    
    exit 0
} else {
    Write-Host "❌ SOME DELIVERABLES ARE MISSING!" -ForegroundColor Red
    Write-Host "Please check the missing files listed above." -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
