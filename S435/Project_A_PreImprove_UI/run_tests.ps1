param(
    [int]$Port=8000,
    [int]$Repeat=3
)

python server/server.py --port $Port &
$PID = $LASTEXITCODE
Start-Sleep -Seconds 1
python -m pytest tests/test_pre_ui.py -- --port $Port --repeat $Repeat
Stop-Process -Id $PID -ErrorAction SilentlyContinue
