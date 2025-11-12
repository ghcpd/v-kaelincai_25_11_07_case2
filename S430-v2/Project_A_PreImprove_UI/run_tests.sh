@echo off
setlocal
set FLASK_APP=server/server.py
if not exist .venv (python -m venv .venv && .\.venv\Scripts\pip.exe install -r requirements.txt && .\.venv\Scripts\playwright.exe install)
start /B .\.venv\Scripts\python.exe server/server.py > logs/log_pre.txt 2>&1
timeout /t 2 > nul
set LATENCY=%1
if "%LATENCY%"=="" set LATENCY=50
set REPEAT=%2
if "%REPEAT%"=="" set REPEAT=1
python - <<'PY'
from playwright.sync_api import sync_playwright
import json, time, os
from pathlib import Path
p=Path('.')
cases = json.loads(Path('../shared_artifacts/test_data.json').read_text())
with sync_playwright() as pw:
    browser = pw.chromium.launch()
    for i in range(int(os.environ.get('REPEAT', '1'))):
        for case in cases:
            print('Running case', case['id'], 'iteration', i+1)
            page = browser.new_page()
            lat = case['env'].get('networkLatency', 50)
            size = case['env'].get('tagCount', 10)
            page.goto(f'http://localhost:8001/?lat={lat}&size={size}')
        page.click('#openModal')
        # wait until window.modalReadyAt set
        page.wait_for_function('window.modalReadyAt !== undefined', timeout=60000)
        modal_load = page.evaluate('window.modalReadyAt - window.modalOpenAt')
        first_visible = page.evaluate("(function(){var t=document.getElementById('title'); return (t && t.getBoundingClientRect().top < window.innerHeight);})()")
        tags_loaded = page.evaluate('document.querySelectorAll("#tagList .tag").length')
        attaches_loaded = page.evaluate('document.querySelectorAll("#attachList .attach").length')
        # create
        page.fill('#title', case['input'].get('title','Test'))
        page.click('button[type="submit"]')
        try:
            page.wait_for_function('window.taskDoneAt !== undefined', timeout=20000)
            task_create = page.evaluate('window.taskDoneAt - window.modalOpenAt')
            task_success = page.evaluate('typeof window.taskError === "undefined"')
        except Exception:
            task_create = None
            task_success = False
        # a11y snapshot for the accessibility case
        a11y = None
        if case['id']=='accessibility':
            try:
                a11y = page.accessibility.snapshot()
            except Exception:
                a11y = None
        out = {'id': case['id'], 'modal_load_ms': modal_load, 'title_visible': first_visible, 'task_create_ms': task_create, 'task_success': task_success, 'tags_loaded': tags_loaded, 'attachments_loaded': attaches_loaded, 'a11y': a11y}
        Path(f'results/results_pre_{case["id"]}.json').write_text(json.dumps(out, indent=2))
        page.screenshot(path=f'screenshots/screenshot_pre_{case["id"]}.png', full_page=True)
        page.close()
    browser.close()
PY
echo Results saved to results\
