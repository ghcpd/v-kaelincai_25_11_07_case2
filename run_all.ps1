# PowerShell script to run both projects and generate comparison report on Windows

param(
    [int]$NetworkDelay = 0,
    [int]$Repeat = 1,
    [string]$TestData = "test_data.json"
)

$ErrorActionPreference = "Stop"

Write-Host "=========================================="
Write-Host "UI/UX Improvement Evaluation"
Write-Host "=========================================="
Write-Host "Network delay: ${NetworkDelay}ms"
Write-Host "Repeat count: $Repeat"
Write-Host "Test data: $TestData"
Write-Host ""

# Create results directory
New-Item -ItemType Directory -Force -Path "results" | Out-Null

# Run Project A (Pre-Improvement)
Write-Host "=========================================="
Write-Host "Running Project A (Pre-Improvement)..."
Write-Host "=========================================="
Push-Location Project_A_PreImprove_UI
& .\run_tests.ps1 -Port 8000 -NetworkDelay $NetworkDelay -Repeat $Repeat -TestData "..\$TestData"
Pop-Location

# Run Project B (Post-Improvement)
Write-Host ""
Write-Host "=========================================="
Write-Host "Running Project B (Post-Improvement)..."
Write-Host "=========================================="
Push-Location Project_B_PostImprove_UI
& .\run_tests.ps1 -Port 8001 -NetworkDelay $NetworkDelay -Repeat $Repeat -TestData "..\$TestData"
Pop-Location

# Generate comparison report
Write-Host ""
Write-Host "=========================================="
Write-Host "Generating comparison report..."
Write-Host "=========================================="
python generate_compare_report.py --test-data $TestData

Write-Host ""
Write-Host "=========================================="
Write-Host "Evaluation complete!"
Write-Host "=========================================="
Write-Host "Results saved in: results\"
Write-Host "Comparison report: compare_report.md"
Write-Host ""

