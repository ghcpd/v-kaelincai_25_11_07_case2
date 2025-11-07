# Master script to run both projects and generate comparison report

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "UI/UX Improvement Evaluation - Full Test Suite" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$workspaceRoot = $PSScriptRoot
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"

# Create results directory
Write-Host "Creating results directory..." -ForegroundColor Yellow
$resultsDir = Join-Path $workspaceRoot "results"
New-Item -ItemType Directory -Force -Path $resultsDir | Out-Null

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "STEP 1: Running Project A (Pre-Improvement)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location (Join-Path $workspaceRoot "Project_A_PreImprove_UI")
& ".\run_tests.ps1"

$projectAExitCode = $LASTEXITCODE

if ($projectAExitCode -ne 0) {
    Write-Host ""
    Write-Host "WARNING: Project A tests completed with errors" -ForegroundColor Yellow
}

# Copy results to shared directory
Write-Host ""
Write-Host "Copying Project A results..." -ForegroundColor Yellow
Copy-Item "results\results_pre.json" "$resultsDir\results_pre.json" -Force
Copy-Item "logs\log_pre.txt" "$resultsDir\log_pre.txt" -Force

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "STEP 2: Running Project B (Post-Improvement)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location (Join-Path $workspaceRoot "Project_B_PostImprove_UI")
& ".\run_tests.ps1"

$projectBExitCode = $LASTEXITCODE

if ($projectBExitCode -ne 0) {
    Write-Host ""
    Write-Host "WARNING: Project B tests completed with errors" -ForegroundColor Yellow
}

# Copy results to shared directory
Write-Host ""
Write-Host "Copying Project B results..." -ForegroundColor Yellow
Copy-Item "results\results_post.json" "$resultsDir\results_post.json" -Force
Copy-Item "logs\log_post.txt" "$resultsDir\log_post.txt" -Force

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "STEP 3: Generating Comparison Report" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $workspaceRoot
python compare_results.py

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "COMPLETE!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "All artifacts saved to:" -ForegroundColor Yellow
Write-Host "  - Aggregated Results: $resultsDir" -ForegroundColor White
Write-Host "  - Comparison Report: $workspaceRoot\compare_report.md" -ForegroundColor White
Write-Host "  - Project A Screenshots: $workspaceRoot\Project_A_PreImprove_UI\screenshots\" -ForegroundColor White
Write-Host "  - Project B Screenshots: $workspaceRoot\Project_B_PostImprove_UI\screenshots\" -ForegroundColor White
Write-Host ""

# Display quick summary
if ((Test-Path "$resultsDir\aggregated_metrics.json")) {
    Write-Host "Quick Summary:" -ForegroundColor Green
    $aggregated = Get-Content "$resultsDir\aggregated_metrics.json" | ConvertFrom-Json
    
    if ($aggregated.improvements) {
        Write-Host ""
        Write-Host "Performance Improvements:" -ForegroundColor Cyan
        foreach ($metric in $aggregated.improvements.PSObject.Properties) {
            if ($metric.Value -is [PSCustomObject] -and $metric.Value.improvement_percent) {
                $color = if ($metric.Value.improvement_percent -gt 0) { "Green" } else { "Red" }
                Write-Host "  $($metric.Name): $($metric.Value.improvement_percent)%" -ForegroundColor $color
            }
        }
    }
}

Write-Host ""
Write-Host "Open compare_report.md to see the full analysis!" -ForegroundColor Yellow
Write-Host ""
