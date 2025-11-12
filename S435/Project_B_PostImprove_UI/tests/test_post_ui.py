"""
Automated tests for Project B - Post-Improvement UI
Use Playwright to measure timings and verify lazy loading and field prioritization.
"""
import json
import os
import time
import asyncio
from pathlib import Path
import argparse

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / 'data' / 'sample_data.json'
RESULTS_DIR = ROOT / 'results'
SCREENSHOT_DIR = ROOT / 'screenshots'
LOG_FILE = ROOT / 'logs' / 'log_post.txt'
RESULTS_FILE = RESULTS_DIR / 'results_post.json'

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

with open(DATA_FILE, 'r') as f:
    sample_data = json.load(f)

async def run_test_case(playwright, case, index, args):
    browser = await playwright.chromium.launch(headless=not args.debug)
    context = await browser.new_context()
    page = await context.new_page()
    timing = {}
    try:
        await page.goto(f"http://127.0.0.1:{args.port}/index.html")
        await page.wait_for_load_state('networkidle')
        await page.evaluate("(latency) => localStorage.setItem('simulated_latency_ms', latency)", str(case['environment'].get('network_latency_ms', 150)))

        # Stabilize
        await page.wait_for_timeout(200)
        start = time.perf_counter()
        await page.click('#createTaskBtn')
        timing['modal_open_ms'] = int((time.perf_counter() - start) * 1000)

        # Step 1: title/due date should be visible immediately and without scrolling
        try:
            await page.wait_for_selector('#title', timeout=5000)
            timing['time_to_title_visible_ms'] = int((time.perf_counter() - start) * 1000)
            title_box = await page.locator('#title').bounding_box()
            viewport_height = await page.evaluate('() => window.innerHeight')
            timing['title_visible_without_scroll'] = title_box['y'] >= 0 and (title_box['y'] + title_box['height']) <= viewport_height
        except Exception as e:
            timing['time_to_title_visible_ms'] = -1
            timing['title_visible_without_scroll'] = False

        # fill step 1
        await page.fill('#title', case['input'].get('title', ''))
        await page.fill('#description', case['input'].get('description') or '')
        if case['input'].get('due_date'):
            await page.fill('#dueDate', case['input']['due_date'])

        # Next to assignment - should load assignee list lazy
        await page.click('#nextToAssignee')
        await page.wait_for_selector('#assignee', timeout=5000)

        # step 2 - assignee should be accessible
        try:
            timing['assignee_loaded'] = await page.evaluate('() => document.querySelectorAll("#assignee option").length > 1')
        except Exception:
            timing['assignee_loaded'] = False

        await page.select_option('#assignee', index='1') if page.query_selector('#assignee option[value="1"]') else None

        # go to tags - should lazy load tags and attachments
        await page.click('#nextToTags')
        await page.wait_for_selector('#tagsContainer .tag-item', timeout=10000)
        timing['tags_loaded'] = await page.evaluate('() => document.querySelectorAll("#tagsContainer .tag-item").length > 0')

        # submit
        await page.click('#submitTask')
        # intercept alert
        try:
            dialog = await page.wait_for_event('dialog', timeout=5000)
            await dialog.dismiss()
            timing['task_created'] = True
        except Exception:
            timing['task_created'] = False

        # screenshot
        screenshot_first = SCREENSHOT_DIR / f"screenshot_post_{case['id']}_first.png"
        await page.screenshot(path=str(screenshot_first), full_page=False)
        screenshot_final = SCREENSHOT_DIR / f"screenshot_post_{case['id']}_final.png"
        await page.screenshot(path=str(screenshot_final), full_page=True)

    except Exception as e:
        timing['error'] = str(e)
    finally:
        await context.close()
        await browser.close()
    return timing


async def run_all(args):
    results = {}
    async with async_playwright() as p:
        for case in sample_data['test_cases']:
            timings_per_run = []
            for i in range(args.repeat):
                t = await run_test_case(p, case, i, args)
                timings_per_run.append(t)
                await asyncio.sleep(0.2)
            results[case['id']] = timings_per_run
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8001)
    parser.add_argument('--repeat', type=int, default=1)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    with open(LOG_FILE, 'w') as lf:
        lf.write('Starting post-improvement tests\n')

    asyncio.run(run_all(args))
    with open(LOG_FILE, 'a') as lf:
        lf.write('Tests completed\n')
