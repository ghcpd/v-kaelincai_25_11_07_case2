@echo off
set REPEAT=%1
if "%REPEAT%"=="" set REPEAT=1
if not exist .venv ( python -m venv .venv & .venv\Scripts\pip install -r requirements.txt & .venv\Scripts\python -m playwright install chromium )
start /B python server\server.py
ping -n 3 127.0.0.1 >nul
.venv\Scripts\python -u tests\test_post_ui.py
copy results\results_post.json ..\shared\results\results_post.json
for /f "tokens=5" %%a in ('netstat -a -n -o ^| findstr :5002') do taskkill /pid %%a /f >nul 2>nul
