import os, json, time, subprocess, requests
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
RESULTS_PATH = ROOT / 'results' / 'results_post.json'
SCREENSHOTS = ROOT / 'screenshots'
DATA_PATH = Path(ROOT.parent) / 'test_data.json'

SERVER_CMD = ['python', str(ROOT / 'server' / 'server.py')]

def start_server():
    proc = subprocess.Popen(SERVER_CMD, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for i in range(20):
        try:
            r = requests.get('http://localhost:5002/')
            if r.status_code == 200:
                return proc
        except Exception:
            time.sleep(0.5)
    raise RuntimeError('Server failed to start')

def stop_server(proc):
    proc.terminate(); proc.wait(timeout=3)

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
                page = browser.new_page(viewport={'width':1200, 'height':800})
                delay = case['env'].get('delay', 0)
                attachments_size = case['env'].get('attachments_size', 1)
                dataset_size = case['env'].get('dataset_size', 10)
                url = f"http://localhost:5002/?delay={delay}&attachments_size={attachments_size}&dataset_size={dataset_size}"
                page.goto(url)
                time.sleep(0.1)
                # Start measuring wizard open
                start = time.time()
                page.click('#openWizard')
                page.wait_for_selector('#wizard', state='visible', timeout=15000)
                wizard_open_ms = int((time.time() - start) * 1000)
                first_screen = SCREENSHOTS / f"screenshots_post_{case['id']}_run{run_idx}_first.png"
                page.screenshot(path=str(first_screen))
                # At initial wizard, tags and attachments should NOT be loaded
                try:
                    tags_options = page.query_selector_all('#tags option')
                    attachments_items = page.query_selector_all('#attachments > div')
                except Exception:
                    tags_options = []
                    attachments_items = []
                tags_loaded_initial = len(tags_options) > 0
                attachments_loaded_initial = len(attachments_items) > 0
                # accessibility checks for step1
                aria_title = page.get_attribute('#title', 'aria-label')
                aria_due = page.get_attribute('#due', 'aria-label')
                # keyboard navigation
                page.keyboard.press('Tab')
                first_tab = page.evaluate("() => document.activeElement.id")
                page.keyboard.press('Tab')
                second_tab = page.evaluate("() => document.activeElement.id")
                # Go to step 2, measure load
                page.click('#next1')
                # wait short time for lazy loads
                time.sleep(0.1 + delay/1000.0)
                tags_loaded_after = len(page.query_selector_all('#tags option')) > 0
                assignees_loaded_after = len(page.query_selector_all('#assignees option')) > 0
                # go to step 3
                page.click('#next2')
                time.sleep(0.1 + delay/1000.0)
                attachments_loaded_after = len(page.query_selector_all('#attachments > div')) > 0
                # Fill required fields in step 1 (title)
                page.fill('#title', case['payload'].get('title') or '')
                # go back to step3 and create
                page.click('#createTask')
                # measure create operation (approx)
                start_create = time.time()
                # wait for dialog
                time.sleep(0.3)
                create_ms = int((time.time() - start_create) * 1000)
                final_screen = SCREENSHOTS / f"screenshots_post_{case['id']}_run{run_idx}_final.png"
                page.screenshot(path=str(final_screen))
                page.close()
                case_results['runs'].append({
                    'wizard_open_ms': wizard_open_ms,
                    'tags_loaded_initial': tags_loaded_initial,
                    'attachments_loaded_initial': attachments_loaded_initial,
                    'tags_loaded_after': tags_loaded_after,
                    'assignees_loaded_after': assignees_loaded_after,
                    'attachments_loaded_after': attachments_loaded_after,
                    'create_ms': create_ms
                })
            results.append(case_results)
        browser.close()
    with open(RESULTS_PATH, 'w') as f:
        json.dump(results, f, indent=2)
    stop_server(proc)
    print('Post-improvement tests finished. Results written to', RESULTS_PATH)
