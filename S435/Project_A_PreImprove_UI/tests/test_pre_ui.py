"""
Automated tests for Project A - Pre-Improvement UI

This script uses Playwright to automate browser interactions and measure timings for the problematic modal.
Run with: python -m pytest tests/test_pre_ui.py
"""
import json
import os
import time
import argparse
import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / 'data' / 'sample_data.json'
RESULTS_DIR = ROOT / 'results'
SCREENSHOT_DIR = ROOT / 'screenshots'
LOG_FILE = ROOT / 'logs' / 'log_pre.txt'

RESULTS_FILE = RESULTS_DIR / 'results_pre.json'

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = Path(LOG_FILE)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

with open(DATA_FILE, 'r') as f:
    sample_data = json.load(f)

async def run_test_case(playwright, case, index, args):
    browser = await playwright.chromium.launch(headless=not args.debug)
    context = await browser.new_context()
    page = await context.new_page()
    timing = {}
    try:
        # configure simulated latency via localStorage and set in page
        await page.goto(f"http://127.0.0.1:{args.port}/index.html")
        await page.wait_for_load_state('networkidle')
        await page.evaluate("(latency) => localStorage.setItem('simulated_latency_ms', latency)", str(case['environment'].get('network_latency_ms', 150)))

        # wait a short bit to let the page stabilize
        await page.wait_for_timeout(200)

        start = time.perf_counter()
        # start open modal
        await page.click('#createTaskBtn')

        # measure modal open time by waiting for modal to be visible
        modal_visible_start = time.perf_counter()
        await page.wait_for_selector('#taskModal', timeout=20000)
        timing['modal_open_ms'] = int((time.perf_counter() - start) * 1000)

        # measure time to first visible input (title) - in pre-improve it's at the bottom
        visible_start = time.perf_counter()
        try:
            await page.wait_for_selector('#title', timeout=10000)
            timing['time_to_title_visible_ms'] = int((time.perf_counter() - start) * 1000)
            # check if visible without scrolling
            title_box = await page.locator('#title').bounding_box()
            viewport_height = await page.evaluate('() => window.innerHeight')
            timing['title_visible_without_scroll'] = title_box['y'] >= 0 and (title_box['y'] + title_box['height']) <= viewport_height
        except Exception as e:
            timing['time_to_title_visible_ms'] = -1
            timing['title_visible_without_scroll'] = False

        # fill out the form using normal fields and submit
        await page.fill('#title', case['input'].get('title', ''))
        await page.fill('#description', case['input'].get('description') or '')
        # note: assignee may be a select option
        try:
            await page.select_option('#assignee', label=case['input'].get('assignee', ''))
        except Exception:
            pass

        # due date
        if case['input'].get('due_date'):
            await page.fill('#dueDate', case['input']['due_date'])

        submit_start = time.perf_counter()
        await page.click(".form-actions .btn-primary")
        # wait for JS alert on success
        try:
            dialog = await page.wait_for_event('dialog', timeout=5000)
            await dialog.dismiss()
            timing['task_create_ms'] = int((time.perf_counter() - submit_start) * 1000)
            timing['task_created'] = True
        except Exception:
            timing['task_create_ms'] = -1
            timing['task_created'] = False

        # check for JS errors
        js_errors = await page.evaluate('window._errors || []')
        timing['js_errors'] = js_errors

        # screenshot first screen
        screenshot_first = SCREENSHOT_DIR / f"screenshot_pre_{case['id']}_first.png"
        await page.screenshot(path=str(screenshot_first), full_page=False)

        # screenshot final
        screenshot_final = SCREENSHOT_DIR / f"screenshot_pre_{case['id']}_final.png"
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
                # short wait between repeats
                await asyncio.sleep(0.2)
            results[case['id']] = timings_per_run
    # write results
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--repeat', type=int, default=1)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    # basic logging
    with open(LOG_FILE, 'w') as lf:
        lf.write('Starting pre-improvement tests\n')

    asyncio.run(run_all(args))
    with open(LOG_FILE, 'a') as lf:
        lf.write('Tests completed\n')
