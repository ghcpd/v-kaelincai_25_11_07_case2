from playwright.sync_api import sync_playwright
import time, json, sys

results = {}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # capture console messages (modal log)
    modal_time = None
    def on_console(msg):
        global modal_time
        text = msg.text()
        if 'Modal open took' in text:
            modal_time = int(text.split()[-2])
    page.on('console', on_console)

    page.goto('http://localhost:5001')
    t0 = time.time()
    page.click('#openModal')
    # wait for title input to be visible
    page.wait_for_selector('#title', timeout=10000)
    t1 = time.time()
    results['time_to_title_visible_ms'] = int((t1-t0)*1000)
    # get modal printed time
    results['modal_open_reported_ms'] = modal_time

    # Create task
    start = time.time()
    page.fill('#title','Test task')
    page.fill('#due','2025-12-31')
    page.click('form button[type="submit"]')
    # wait for alert auto-hidden by script, we can't intercept; just wait short
    time.sleep(1)
    end = time.time()
    results['task_create_ms'] = int((end-start)*1000)

    with open('../results/results_pre.json','w') as f:
        json.dump(results, f, indent=2)

    browser.close()

print('Pre results saved')
