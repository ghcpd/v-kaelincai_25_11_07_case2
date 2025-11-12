import os, json, time, subprocess, requests, signal
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
RESULTS_PATH = ROOT / 'results' / 'results_pre.json'
SCREENSHOTS = ROOT / 'screenshots'
DATA_PATH = Path(ROOT.parent) / 'test_data.json'

SERVER_CMD = ['python', str(ROOT / 'server' / 'server.py')]

def start_server():
    # start server in background; log is written by server
    proc = subprocess.Popen(SERVER_CMD, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # wait for server to be responsive
    for i in range(20):
        try:
            r = requests.get('http://localhost:5001/')
            if r.status_code == 200:
                return proc
        except Exception:
            time.sleep(0.5)
    raise RuntimeError('Server failed to start')

def stop_server(proc):
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except Exception:
        proc.kill()

def is_element_in_viewport(page, selector):
    box = page.query_selector(selector).bounding_box()
    viewport = page.viewport_size
    if not box: return False
    return box['y'] >= 0 and (box['y'] + box['height']) <= viewport['height']

if __name__ == '__main__':
    with open(DATA_PATH) as f:
        cases = json.load(f)

    proc = start_server()

    results = []
    repeat = int(os.environ.get('REPEAT', '1'))
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for case in cases:
            case_results = {'id': case['id'], 'runs': []}
            for run_idx in range(repeat):
                page = browser.new_page(viewport={'width': 1200, 'height': 800})
                delay = case['env'].get('delay', 0)
                attachments_size = case['env'].get('attachments_size', 1)
                dataset_size = case['env'].get('dataset_size', 10)
                url = f"http://localhost:5001/?delay={delay}&attachments_size={attachments_size}&dataset_size={dataset_size}"
                page.goto(url)
                # Wait a moment for base UI
                time.sleep(0.1)
                # Start measuring modal open
                start = time.time()
                page.click('#openModal')
                page.wait_for_selector('#modal', state='visible', timeout=15000)
                modal_open_ms = int((time.time() - start) * 1000)
                # take screenshot first screen
                first_screen = SCREENSHOTS / f"screenshots_pre_{case['id']}_run{run_idx}_first.png"
                page.screenshot(path=str(first_screen))

                # Check whether title is visible in first screen
                title_visible = is_element_in_viewport(page, '#title')
                due_visible = is_element_in_viewport(page, '#due')
                first_field_visible = title_visible or due_visible

                # Accessibility checks: labels presence and keyboard navigation
                aria_title = page.get_attribute('#title', 'aria-label')
                aria_due = page.get_attribute('#due', 'aria-label')
                # keyboard navigation: tab through first few elements
                page.keyboard.press('Tab')
                first_tab = page.evaluate("() => document.activeElement.id")
                page.keyboard.press('Tab')
                second_tab = page.evaluate("() => document.activeElement.id")
                page.keyboard.press('Tab')
                third_tab = page.evaluate("() => document.activeElement.id")

                # Fill fields (scroll if needed)
                # Ensure title is filled
                try:
                    page.fill('#title', case['payload'].get('title') or '')
                except Exception:
                    # maybe not interactable yet, scroll to bottom
                    page.evaluate("() => document.querySelector('#modal .modal-content').scrollTop = 1000")
                    page.fill('#title', case['payload'].get('title') or '')

                # Fill others
                page.fill('#description', str(case['payload'].get('description') or ''))
                if case['payload'].get('assignee'):
                    page.select_option('#assignees', label=case['payload'].get('assignee'))
                if case['env'].get('delay', 0) > 0:
                    # let background loads finish for eager version
                    time.sleep(case['env'].get('delay', 0)/1000.0 + 0.1)
                # Create task and measure time to success dialog
                start_create = time.time()
                # capture dialog
                dialog_future = []
                def on_dialog(dialog):
                    dialog_future.append(dialog.message)
                    dialog.dismiss()
                page.on('dialog', on_dialog)
                page.click('#createTask')
                # wait a little longer for server response
                time.sleep(0.3)
                # assume dialog appeared
                create_ms = int((time.time() - start_create) * 1000)
                # take final screenshot
                final_screen = SCREENSHOTS / f"screenshots_pre_{case['id']}_run{run_idx}_final.png"
                page.screenshot(path=str(final_screen))
                page.close()
                case_results['runs'].append({
                    'modal_open_ms': modal_open_ms,
                    'title_visible': title_visible,
                    'due_visible': due_visible,
                    'create_ms': create_ms,
                    'dialog_messages': dialog_future,
                })
            results.append(case_results)
        browser.close()

    with open(RESULTS_PATH, 'w') as f:
        json.dump(results, f, indent=2)

    stop_server(proc)
    print('Pre-improvement tests finished. Results written to', RESULTS_PATH)
