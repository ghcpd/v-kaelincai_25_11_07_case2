from playwright.sync_api import sync_playwright
import time, json

results = {}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto('http://localhost:5002')
    t0=time.time()
    page.click('#openWizard')
    page.wait_for_selector('#title', timeout=10000)
    t1=time.time()
    results['time_to_title_visible_ms'] = int((t1-t0)*1000)

    # go next to trigger members lazy load
    page.fill('#title','Improved Task')
    page.fill('#due','2025-12-31')
    page.click('#next1')
    # wait for assignee options populated
    page.wait_for_selector('#assignee option', timeout=5000)
    # go next to final
    page.click('#next2')
    # wait for tags to show
    page.wait_for_selector('#lazy-tags span', timeout=5000)
    start=time.time()
    page.click('#finish')
    time.sleep(1)
    end=time.time()
    results['task_create_ms'] = int((end-start)*1000)
    with open('../results/results_post.json','w') as f:
        json.dump(results,f,indent=2)
    browser.close()

print('Post results saved')
