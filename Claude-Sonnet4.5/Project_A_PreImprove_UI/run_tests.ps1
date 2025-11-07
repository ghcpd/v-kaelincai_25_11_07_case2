# PowerShell script to run tests for Project A (Pre-Improvement UI)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Project A - Pre-Improvement UI Test Runner" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

# Change to project root
Set-Location $projectRoot

# Create/activate virtual environment
Write-Host "Setting up Python environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    python -m venv venv
}

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# Install Playwright browsers if needed
Write-Host "Installing Playwright browsers..." -ForegroundColor Yellow
playwright install chromium --with-deps

# Create output directories
Write-Host "Creating output directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "screenshots" | Out-Null
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
New-Item -ItemType Directory -Force -Path "results" | Out-Null

# Clear previous results
Write-Host "Clearing previous test results..." -ForegroundColor Yellow
Remove-Item -Path "screenshots\*.png" -ErrorAction SilentlyContinue
Remove-Item -Path "logs\*.txt" -ErrorAction SilentlyContinue
Remove-Item -Path "results\*.json" -ErrorAction SilentlyContinue

# Start server in background
Write-Host "Starting HTTP server on port 8001..." -ForegroundColor Yellow
$serverJob = Start-Job -ScriptBlock {
    param($serverPath)
    Set-Location $serverPath
    python server.py 8001
} -ArgumentList "$projectRoot\server"

# Wait for server to start
Start-Sleep -Seconds 3

# Test server connectivity
Write-Host "Testing server connectivity..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001" -UseBasicParsing -TimeoutSec 5
    Write-Host "Server is running!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Server failed to start!" -ForegroundColor Red
    Stop-Job $serverJob
    Remove-Job $serverJob
    exit 1
}

# Run tests
Write-Host ""
Write-Host "Running test suite..." -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
python tests\test_pre_ui.py

$testExitCode = $LASTEXITCODE

# Stop server
Write-Host ""
Write-Host "Stopping server..." -ForegroundColor Yellow
Stop-Job $serverJob
Remove-Job $serverJob

# Print results summary
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Test Execution Complete" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Results saved to:" -ForegroundColor Yellow
Write-Host "  - Screenshots: $projectRoot\screenshots\" -ForegroundColor White
Write-Host "  - Logs: $projectRoot\logs\log_pre.txt" -ForegroundColor White
Write-Host "  - Results JSON: $projectRoot\results\results_pre.json" -ForegroundColor White
Write-Host ""

# Check if results exist
if (Test-Path "$projectRoot\results\results_pre.json") {
    $results = Get-Content "$projectRoot\results\results_pre.json" | ConvertFrom-Json
    Write-Host "Test Summary:" -ForegroundColor Green
    Write-Host "  Total Tests: $($results.total_tests)" -ForegroundColor White
    Write-Host "  Passed: $($results.passed)" -ForegroundColor Green
    Write-Host "  Failed: $($results.failed)" -ForegroundColor $(if ($results.failed -gt 0) { "Red" } else { "White" })
    Write-Host ""
}

exit $testExitCode
