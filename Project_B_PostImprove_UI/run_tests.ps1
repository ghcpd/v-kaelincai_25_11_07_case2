# PowerShell script to run tests for Project B (Post-Improvement) on Windows

param(
    [int]$Port = 8001,
    [int]$NetworkDelay = 0,
    [int]$Repeat = 1,
    [string]$TestData = "data\test_data.json"
)

$ErrorActionPreference = "Stop"

Write-Host "Starting Project B (Post-Improvement) tests..."
Write-Host "Port: $Port"
Write-Host "Network delay: ${NetworkDelay}ms"
Write-Host "Repeat count: $Repeat"

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
}

# Start server in background
Write-Host "Starting server on port $Port..."
$serverJob = Start-Job -ScriptBlock {
    param($port, $delay, $testData)
    Set-Location $using:PWD
    python server\server.py --port $port --network-delay $delay --test-data $testData
} -ArgumentList $Port, $NetworkDelay, $TestData

# Wait for server to start
Start-Sleep -Seconds 2

# Run tests
Write-Host "Running tests..."
python tests\test_post_ui.py --url "http://localhost:$Port" --network-delay $NetworkDelay --repeat $Repeat --test-data $TestData

$testExitCode = $LASTEXITCODE

# Stop server
Write-Host "Stopping server..."
Stop-Job $serverJob
Remove-Job $serverJob

exit $testExitCode

