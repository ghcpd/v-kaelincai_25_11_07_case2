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

def run_case(case):
    driver = make_driver()
    driver.get('http://127.0.0.1:8002/')
    t0 = time.time()
    driver.find_element(By.ID, 'openWizard').click()
    first_visible = False
    first_ms = None
    for i in range(100):
        try:
            el = driver.find_element(By.ID, 'title')
            if el.is_displayed():
                first_visible = True
                first_ms = int((time.time()-t0)*1000)
                break
        except:
            pass
        time.sleep(0.05)

    # screenshot first screen
    screen1 = os.path.join(SCREEN_DIR, f'screenshots_post_{case["id"]}.png')
    driver.save_screenshot(screen1)

    # Navigate to attachments to ensure lazy load
    try:
        driver.find_element(By.ID, 'nextBtn').click()
        time.sleep(0.2)
        driver.find_element(By.ID, 'nextBtn').click()
    except:
        pass

    time.sleep(0.5)
    screen2 = os.path.join(SCREEN_DIR, f'screenshots_post_{case["id"]}_final.png')
    driver.save_screenshot(screen2)

    total_ms = int((time.time()-t0)*1000)
    # detect whether tags/attachments loaded lazily (we expect they load after initial)
    tags_loaded_initial = False
    try:
        # check if tagsContainer has children in first screen
        pass
    except:
        pass

    result = {
        'id': case['id'],
        'time_to_title_visible_ms': first_ms or -1,
        'task_create_ms': total_ms,
        'screenshot_first': screen1,
        'screenshot_final': screen2
    }
    driver.quit()
    return result

def test_all():
    results = []
    for case in TEST_DATA:
        r = run_case(case)
        results.append(r)
    with open(os.path.join(RESULTS_DIR, 'results_post.json'),'w') as f:
        json.dump(results, f, indent=2)

if __name__=='__main__':
    test_all()
