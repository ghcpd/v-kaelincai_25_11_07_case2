#!/usr/bin/env python3
"""
Test harness for pre-improvement UI.
Measures modal open time, field visibility, and task creation time.
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

BASE_DIR = Path(__file__).parent.parent
TEST_DATA_PATH = BASE_DIR / 'data' / 'test_data.json'
RESULTS_DIR = BASE_DIR / 'results'
SCREENSHOTS_DIR = BASE_DIR / 'screenshots'
LOGS_DIR = BASE_DIR / 'logs'

# Ensure directories exist
RESULTS_DIR.mkdir(exist_ok=True)
SCREENSHOTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

class UITester:
    def __init__(self, base_url='http://localhost:8000', network_delay=0):
        self.base_url = base_url
        self.network_delay = network_delay
        self.results = []
        self.logs = []
    
    def log(self, message):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        self.logs.append(log_entry)
    
    async def measure_modal_open_time(self, page):
        """Measure time from button click to modal visible"""
        start_time = time.time()
        
        # Click create task button
        await page.click('#createTaskBtn')
        
        # Wait for modal to be visible
        await page.wait_for_selector('#taskModal.show', timeout=10000)
        
        modal_open_time = (time.time() - start_time) * 1000
        
        # Wait a bit for content to load
        await page.wait_for_timeout(500)
        
        return modal_open_time
    
    async def measure_time_to_title_visible(self, page):
        """Measure time until title field is visible without scrolling"""
        start_time = time.time()
        
        # Check if title field is in viewport
        title_visible = False
        max_wait = 10  # seconds
        elapsed = 0
        
        while not title_visible and elapsed < max_wait:
            await page.wait_for_timeout(100)
            title_visible = await page.evaluate("""
                () => {
                    const title = document.getElementById('taskTitle');
                    if (!title) return false;
                    const rect = title.getBoundingClientRect();
                    const viewportHeight = window.innerHeight;
                    return rect.top >= 0 && rect.top < viewportHeight;
                }
            """)
            elapsed = time.time() - start_time
        
        time_to_visible = elapsed * 1000
        return time_to_visible, title_visible
    
    async def measure_task_creation_time(self, page, test_case):
        """Measure time to fill form and create task"""
        start_time = time.time()
        
        input_data = test_case.get('input', {})
        
        # Fill in form fields
        if input_data.get('title'):
            await page.fill('#taskTitle', str(input_data['title']))
        
        if input_data.get('description'):
            await page.fill('#taskDescription', str(input_data['description']))
        
        if input_data.get('dueDate'):
            await page.fill('#dueDate', str(input_data['dueDate']))
        
        if input_data.get('priority'):
            await page.select_option('#priority', input_data['priority'])
        
        # Submit form
        await page.click('button[type="submit"]')
        
        # Wait for form submission (check for alert or modal close)
        try:
            await page.wait_for_timeout(500)
            # Check if modal is closed
            modal_closed = await page.evaluate("""
                () => {
                    const modal = document.getElementById('taskModal');
                    return !modal.classList.contains('show');
                }
            """)
            
            if modal_closed:
                task_create_time = (time.time() - start_time) * 1000
                return task_create_time, True
        except Exception as e:
            self.log(f"Error during form submission: {e}")
        
        task_create_time = (time.time() - start_time) * 1000
        return task_create_time, False
    
    async def check_accessibility(self, page):
        """Check accessibility features"""
        checks = {}
        
        # Check for ARIA labels
        aria_labels = await page.evaluate("""
            () => {
                const labels = document.querySelectorAll('[aria-label], label[for]');
                return labels.length > 0;
            }
        """)
        checks['aria_labels_present'] = aria_labels
        
        # Check keyboard navigation (tab order)
        try:
            await page.keyboard.press('Tab')
            focused = await page.evaluate("() => document.activeElement.tagName")
            checks['keyboard_navigable'] = focused in ['INPUT', 'BUTTON', 'SELECT', 'TEXTAREA']
        except:
            checks['keyboard_navigable'] = False
        
        # Check focus visibility
        focus_visible = await page.evaluate("""
            () => {
                const style = window.getComputedStyle(document.activeElement);
                return style.outline !== 'none' || style.outlineWidth !== '0px';
            }
        """)
        checks['focus_visible'] = focus_visible
        
        return checks
    
    async def run_test_case(self, page, test_case):
        """Run a single test case"""
        test_id = test_case['id']
        self.log(f"Running test case: {test_id}")
        
        result = {
            'test_id': test_id,
            'description': test_case.get('description', ''),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'metrics': {},
            'errors': [],
            'passed': False
        }
        
        try:
            # Navigate to page
            await page.goto(self.base_url, wait_until='networkidle')
            await page.wait_for_timeout(500)
            
            # Measure modal open time
            modal_open_time = await self.measure_modal_open_time(page)
            result['metrics']['modal_load_ms'] = round(modal_open_time, 2)
            
            # Take screenshot of first screen
            screenshot_path = SCREENSHOTS_DIR / f'screenshot_pre_{test_id}.png'
            await page.screenshot(path=str(screenshot_path))
            result['screenshot'] = str(screenshot_path.relative_to(BASE_DIR))
            
            # Measure time to title visible
            time_to_title, title_visible = await self.measure_time_to_title_visible(page)
            result['metrics']['time_to_title_visible_ms'] = round(time_to_title, 2)
            result['metrics']['first_field_visible'] = title_visible
            
            # Check accessibility
            if test_id == 'accessibility_case':
                accessibility = await self.check_accessibility(page)
                result['metrics'].update(accessibility)
            
            # Test form submission (skip for malformed inputs)
            if test_id != 'malformed_inputs_case':
                task_create_time, success = await self.measure_task_creation_time(page, test_case)
                result['metrics']['task_create_ms'] = round(task_create_time, 2)
                result['metrics']['task_created_successfully'] = success
            else:
                # Test validation for malformed inputs
                await page.fill('#taskTitle', '')
                await page.fill('#dueDate', '')
                await page.click('button[type="submit"]')
                await page.wait_for_timeout(500)
                
                # Check for validation error
                validation_error = await page.evaluate("""
                    () => {
                        const title = document.getElementById('taskTitle');
                        return title.validity.valid === false;
                    }
                """)
                result['metrics']['validation_error'] = validation_error
                result['metrics']['error_handled_gracefully'] = validation_error
            
            # Evaluate pass/fail based on criteria
            pass_criteria = test_case.get('pass_criteria', {})
            passed = True
            
            for criterion, expected_value in pass_criteria.items():
                actual_value = result['metrics'].get(criterion)
                if isinstance(expected_value, str) and '<' in expected_value:
                    threshold = float(expected_value.replace('<', '').strip())
                    if actual_value is None or actual_value >= threshold:
                        passed = False
                elif actual_value != expected_value:
                    passed = False
            
            result['passed'] = passed
            
        except Exception as e:
            self.log(f"Error in test case {test_id}: {e}")
            result['errors'].append(str(e))
            result['passed'] = False
        
        return result
    
    async def run_all_tests(self, test_cases, repeat_count=1):
        """Run all test cases"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.create_context()
            page = await context.new_page()
            
            # Set network conditions if delay specified
            if self.network_delay > 0:
                await context.route('**/*', lambda route: asyncio.create_task(
                    self.delayed_route(route)
                ))
            
            for iteration in range(repeat_count):
                self.log(f"Test iteration {iteration + 1}/{repeat_count}")
                
                for test_case in test_cases:
                    result = await self.run_test_case(page, test_case)
                    self.results.append(result)
                    
                    # Reset page state
                    await page.goto('about:blank')
                    await page.wait_for_timeout(500)
            
            await browser.close()
    
    async def delayed_route(self, route):
        """Add delay to network requests"""
        await asyncio.sleep(self.network_delay / 1000.0)
        await route.continue_()
    
    def save_results(self):
        """Save test results to JSON"""
        results_path = RESULTS_DIR / 'results_pre.json'
        
        output = {
            'test_run_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'network_delay_ms': self.network_delay,
            'results': self.results,
            'summary': self.compute_summary()
        }
        
        with open(results_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        self.log(f"Results saved to {results_path}")
        return results_path
    
    def compute_summary(self):
        """Compute summary metrics"""
        if not self.results:
            return {}
        
        modal_times = [r['metrics'].get('modal_load_ms', 0) for r in self.results if 'modal_load_ms' in r['metrics']]
        task_times = [r['metrics'].get('task_create_ms', 0) for r in self.results if 'task_create_ms' in r['metrics']]
        
        passed_count = sum(1 for r in self.results if r['passed'])
        total_count = len(self.results)
        
        summary = {
            'total_tests': total_count,
            'passed_tests': passed_count,
            'failed_tests': total_count - passed_count,
            'success_rate': round(passed_count / total_count * 100, 2) if total_count > 0 else 0,
            'avg_modal_load_ms': round(sum(modal_times) / len(modal_times), 2) if modal_times else 0,
            'median_modal_load_ms': round(sorted(modal_times)[len(modal_times) // 2], 2) if modal_times else 0,
            'avg_task_create_ms': round(sum(task_times) / len(task_times), 2) if task_times else 0,
            'median_task_create_ms': round(sorted(task_times)[len(task_times) // 2], 2) if task_times else 0
        }
        
        return summary
    
    def save_logs(self):
        """Save logs to file"""
        log_path = LOGS_DIR / 'log_pre.txt'
        with open(log_path, 'w') as f:
            f.write('\n'.join(self.logs))
        self.log(f"Logs saved to {log_path}")

async def main():
    import argparse
    parser = argparse.ArgumentParser(description='Test pre-improvement UI')
    parser.add_argument('--url', default='http://localhost:8000', help='Base URL')
    parser.add_argument('--network-delay', type=int, default=0, help='Network delay in ms')
    parser.add_argument('--repeat', type=int, default=1, help='Repeat count')
    parser.add_argument('--test-data', type=str, default=str(TEST_DATA_PATH), help='Test data JSON path')
    args = parser.parse_args()
    
    # Load test cases
    with open(args.test_data, 'r') as f:
        test_data = json.load(f)
    
    test_cases = test_data.get('test_cases', [])
    
    tester = UITester(base_url=args.url, network_delay=args.network_delay)
    tester.log("Starting pre-improvement UI tests")
    
    await tester.run_all_tests(test_cases, repeat_count=args.repeat)
    
    tester.save_results()
    tester.save_logs()
    
    summary = tester.compute_summary()
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Total tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print(f"Success rate: {summary['success_rate']}%")
    print(f"Avg modal load time: {summary['avg_modal_load_ms']}ms")
    print(f"Avg task creation time: {summary['avg_task_create_ms']}ms")
    print("="*50)

if __name__ == '__main__':
    asyncio.run(main())

