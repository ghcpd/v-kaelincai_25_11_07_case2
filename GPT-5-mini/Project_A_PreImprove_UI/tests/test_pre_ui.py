import json
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RESULTS_DIR = os.path.join(ROOT, 'results')
SCREEN_DIR = os.path.join(ROOT, 'screenshots')
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(SCREEN_DIR, exist_ok=True)

with open(os.path.join(ROOT, '..', 'test_data.json')) as f:
    TEST_DATA = json.load(f)['cases']

def make_driver():
    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--window-size=1200,800')
    return webdriver.Chrome(options=opts)

def run_case(case, idx):
    env = case['env']
    latency = env.get('latency_ms', 0)
    driver = make_driver()
    start = time.time()
    driver.get(f'http://127.0.0.1:8001/?')
    # click open modal and measure time until title input visible
    t0 = time.time()
    driver.find_element(By.ID, 'openModal').click()
    # Wait for eager loads
    title_visible = False
    modal_load_ms = None
    for i in range(100):
        try:
            el = driver.find_element(By.ID, 'title')
            if el.is_displayed():
                modal_load_ms = int((time.time()-t0)*1000)
                title_visible = True
                break
        except:
            pass
        time.sleep(0.05)

    # take screenshot of first screen
    screen1 = os.path.join(SCREEN_DIR, f'screenshots_pre_{case["id"]}.png')
    driver.save_screenshot(screen1)

    # Fill and create (handle malformed)
    try:
        driver.find_element(By.ID, 'title').send_keys(case['input'].get('title',''))
        driver.find_element(By.ID, 'dueDate').send_keys(case['input'].get('dueDate',''))
        driver.find_element(By.ID, 'createBtn').click()
    except Exception as e:
        pass

    total_ms = int((time.time()-t0)*1000)
    result = {
        'id': case['id'],
        'modal_load_ms': modal_load_ms or -1,
        'title_visible': title_visible,
        'task_create_ms': total_ms,
        'screenshot': screen1
    }
    driver.quit()
    return result

def test_all():
    results = []
    for idx, case in enumerate(TEST_DATA):
        r = run_case(case, idx)
        results.append(r)
    with open(os.path.join(RESULTS_DIR, 'results_pre.json'),'w') as f:
        json.dump(results, f, indent=2)

if __name__=='__main__':
    test_all()
