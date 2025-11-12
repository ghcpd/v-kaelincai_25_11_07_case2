@echo off
set REPEAT=%1
if "%REPEAT%"=="" set REPEAT=1
REM setup venv and install if needed
if not exist .venv ( python -m venv .venv & .venv\Scripts\pip install -r requirements.txt & .venv\Scripts\python -m playwright install chromium )
REM Start server 
start /B python server\server.py
REM wait for server to start
ping -n 3 127.0.0.1 >nul
REM run tests
.venv\Scripts\python -u tests\test_pre_ui.py
REM copy results to shared folder
copy results\results_pre.json ..\shared\results\results_pre.json
REM stop server (best-effort)
for /f "tokens=5" %%a in ('netstat -a -n -o ^| findstr :5001') do taskkill /pid %%a /f >nul 2>nul
