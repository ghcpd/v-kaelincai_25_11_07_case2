param(
  [int]$repeat = 3,
  [int]$latency = 0
)
Write-Output "Setting up virtualenv..."
python -m venv .venv; .\.venv\Scripts\pip.exe install -r requirements.txt
Write-Output "Starting server..."
$env:SIM_LATENCY_MS = $latency
Start-Process -NoNewWindow -FilePath .\.venv\Scripts\python.exe -ArgumentList 'server/server.py' -PassThru | Out-File server_pid.txt
Start-Sleep -Seconds 1
Write-Output "Running tests..."
python -m pytest tests -q --capture=tee-sys
Write-Output "Stopping server..."
Get-Content server_pid.txt | ForEach-Object { Stop-Process -Id ($_ ) -ErrorAction SilentlyContinue }
