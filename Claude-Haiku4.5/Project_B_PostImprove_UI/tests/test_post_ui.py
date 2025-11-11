#!/usr/bin/env python3
"""
Test harness for Post-improvement UI (Project B)
Tests the optimized wizard with lazy loading and improved UX
"""

import json
import time
import os
import sys
import subprocess
import threading
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class PostImprovementUITester:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results = []
        self.server_process = None
        self.driver = None
        self.server_port = config.get('server_port', 8002)
        self.base_url = f"http://localhost:{self.server_port}"
        
        # Setup paths
        self.project_root = Path(__file__).parent.parent
        self.logs_dir = self.project_root / 'logs'
        self.screenshots_dir = self.project_root / 'screenshots'
        self.results_dir = self.project_root / 'results'
        
        # Ensure directories exist
        for dir_path in [self.logs_dir, self.screenshots_dir, self.results_dir]:
            dir_path.mkdir(exist_ok=True)
    
    def start_server(self) -> bool:
        """Start the test server"""
        try:
            server_script = self.project_root / 'server' / 'server.py'
            self.server_process = subprocess.Popen(
                [sys.executable, str(server_script), str(self.server_port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            max_attempts = 30
            for _ in range(max_attempts):
                try:
                    response = requests.get(f"{self.base_url}/api/health", timeout=1)
                    if response.status_code == 200:
                        print(f"Server started successfully on port {self.server_port}")
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(1)
            
            print("Failed to start server")
            return False
            
        except Exception as e:
            print(f"Error starting server: {e}")
            return False
    
    def stop_server(self):
        """Stop the test server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait(timeout=10)
            print("Server stopped")
    
    def setup_driver(self, browser: str = 'chrome') -> webdriver.Remote:
        """Setup and return webdriver instance"""
        if browser.lower() == 'chrome':
            options = ChromeOptions()
            if self.config.get('headless', False):
                options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            
            driver = webdriver.Chrome(options=options)
            
        elif browser.lower() == 'firefox':
            options = FirefoxOptions()
            if self.config.get('headless', False):
                options.add_argument('--headless')
            options.add_argument('--width=1920')
            options.add_argument('--height=1080')
            
            driver = webdriver.Firefox(options=options)
        else:
            raise ValueError(f"Unsupported browser: {browser}")
        
        driver.implicitly_wait(10)
        return driver
    
    def simulate_network_conditions(self, latency_ms: int):
        """Simulate network conditions using browser dev tools"""
        if hasattr(self.driver, 'set_network_conditions'):
            # Chrome DevTools Protocol
            self.driver.set_network_conditions(
                offline=False,
                latency=latency_ms,
                throughput=500000  # 500KB/s
            )
    
    def run_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test case"""
        test_id = test_case['test_id']
        print(f"\nRunning test case: {test_id}")
        
        start_time = time.time()
        result = {
            'test_id': test_id,
            'description': test_case['description'],
            'start_time': start_time,
            'status': 'running',
            'metrics': {},
            'screenshots': [],
            'errors': []
        }
        
        try:
            # Setup browser for this test
            browser = test_case['simulated_environment'].get('browser', 'chrome')
            self.driver = self.setup_driver(browser)
            
            # Set network conditions
            network_latency = test_case['simulated_environment'].get('network_latency_ms', 50)
            if hasattr(self.driver, 'set_network_conditions'):
                self.simulate_network_conditions(network_latency)
            
            # Navigate to page with network latency parameter
            url = f"{self.base_url}?network_latency_ms={network_latency}"
            self.driver.get(url)
            
            # Take initial screenshot
            screenshot_path = self.take_screenshot(f"{test_id}_initial")
            result['screenshots'].append(screenshot_path)
            
            # Run the specific test
            if test_case['test_id'] == 'normal_case':
                metrics = self.test_normal_case(test_case)
            elif test_case['test_id'] == 'heavy_data_case':
                metrics = self.test_heavy_data_case(test_case)
            elif test_case['test_id'] == 'slow_network_case':
                metrics = self.test_slow_network_case(test_case)
            elif test_case['test_id'] == 'malformed_inputs_case':
                metrics = self.test_malformed_inputs_case(test_case)
            elif test_case['test_id'] == 'accessibility_keyboard_case':
                metrics = self.test_accessibility_keyboard_case(test_case)
            else:
                raise ValueError(f"Unknown test case: {test_case['test_id']}")
            
            result['metrics'] = metrics
            result['status'] = 'passed'
            
            # Take final screenshot
            screenshot_path = self.take_screenshot(f"{test_id}_final")
            result['screenshots'].append(screenshot_path)
            
        except Exception as e:
            result['status'] = 'failed'
            result['errors'].append(str(e))
            print(f"Test {test_id} failed: {e}")
            
            # Take error screenshot
            if self.driver:
                screenshot_path = self.take_screenshot(f"{test_id}_error")
                result['screenshots'].append(screenshot_path)
        
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
            
            result['end_time'] = time.time()
            result['duration'] = result['end_time'] - result['start_time']
        
        return result
    
    def test_normal_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Test normal task creation flow with wizard"""
        metrics = {}
        
        # Click create task button and measure modal load time
        create_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "createTaskBtn"))
        )
        
        modal_start = time.time()
        create_btn.click()
        
        # Wait for modal to appear (should be instant for improved version)
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "modalOverlay"))
        )
        
        # Wait for first step content (no loading indicator for step 1)
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "step1"))
        )
        
        modal_end = time.time()
        metrics['modal_load_ms'] = (modal_end - modal_start) * 1000
        
        # Check if title field is immediately visible (improved UX)
        title_field = WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "title"))
        )
        
        title_visible_time = time.time()
        metrics['time_to_title_visible_ms'] = (title_visible_time - modal_start) * 1000
        
        # Title should be visible without scrolling (improved)
        title_location = title_field.location['y']
        viewport_height = self.driver.execute_script("return window.innerHeight")
        scroll_position = self.driver.execute_script("return window.pageYOffset")
        
        metrics['title_visible_without_scroll'] = (
            title_location >= scroll_position and 
            title_location <= scroll_position + viewport_height
        )
        
        # Fill out step 1 - essential fields
        task_data = test_case['input_payload']
        
        title_field.clear()
        title_field.send_keys(task_data['title'])
        
        # Fill due date
        due_date_field = self.driver.find_element(By.ID, "dueDate")
        due_date_field.send_keys(task_data['due_date'])
        
        # Fill priority
        priority_select = self.driver.find_element(By.ID, "priority")
        priority_select.send_keys(task_data['priority'])
        
        # Fill description
        desc_field = self.driver.find_element(By.ID, "description")
        desc_field.send_keys(task_data['description'])
        
        # Move to step 2 - this should trigger lazy loading
        next_btn = self.driver.find_element(By.ID, "nextBtn")
        next_btn.click()
        
        # Wait for step 2 to load
        WebDriverWait(self.driver, 15).until(
            EC.visibility_of_element_located((By.ID, "step2"))
        )
        
        # Check if lazy loading occurred for step 2
        try:
            WebDriverWait(self.driver, 2).until(
                EC.invisibility_of_element_located((By.ID, "assignmentLoading"))
            )
            metrics['step2_lazy_loaded'] = True
        except TimeoutException:
            metrics['step2_lazy_loaded'] = False
        
        # Fill assignee if available
        try:
            assignee_select = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "assignee"))
            )
            assignee_select.send_keys(task_data['assignee'])
        except TimeoutException:
            pass
        
        # Move to step 3
        next_btn = self.driver.find_element(By.ID, "nextBtn")
        next_btn.click()
        
        # Wait for step 3 to load
        WebDriverWait(self.driver, 15).until(
            EC.visibility_of_element_located((By.ID, "step3"))
        )
        
        # Check if lazy loading occurred for step 3
        try:
            WebDriverWait(self.driver, 2).until(
                EC.invisibility_of_element_located((By.ID, "additionalLoading"))
            )
            metrics['step3_lazy_loaded'] = True
        except TimeoutException:
            metrics['step3_lazy_loaded'] = False
        
        # Submit the form
        submit_start = time.time()
        submit_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "submitBtn"))
        )
        submit_btn.click()
        
        # Wait for success indication
        time.sleep(2)  # Allow for submission processing
        
        submit_end = time.time()
        metrics['task_create_ms'] = (submit_end - modal_start) * 1000
        
        # Check accessibility score
        metrics['accessibility_score'] = self.calculate_accessibility_score()
        
        return metrics
    
    def test_heavy_data_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Test with heavy data to verify lazy loading effectiveness"""
        metrics = self.test_normal_case(test_case)
        
        # Verify lazy loading is functional (should be True for post-improvement)
        metrics['tags_lazy_loaded'] = metrics.get('step3_lazy_loaded', False)
        metrics['attachments_lazy_loaded'] = metrics.get('step3_lazy_loaded', False)
        
        return metrics
    
    def test_slow_network_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Test with slow network conditions to verify progressive loading"""
        metrics = self.test_normal_case(test_case)
        
        # Check for progressive loading indicators
        try:
            # Check if loading indicators are shown for lazy-loaded steps
            self.driver.get(f"{self.base_url}?network_latency_ms=500")
            
            # Open wizard
            create_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "createTaskBtn"))
            )
            create_btn.click()
            
            # Fill step 1 quickly
            title_field = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "title"))
            )
            title_field.send_keys("Test task")
            
            due_date_field = self.driver.find_element(By.ID, "dueDate")
            due_date_field.send_keys("2025-12-31")
            
            priority_select = self.driver.find_element(By.ID, "priority")
            priority_select.send_keys("high")
            
            # Move to step 2 and check for loading indicator
            next_btn = self.driver.find_element(By.ID, "nextBtn")
            next_btn.click()
            
            # Should see loading indicator briefly
            try:
                loading_indicator = WebDriverWait(self.driver, 2).until(
                    EC.visibility_of_element_located((By.ID, "assignmentLoading"))
                )
                metrics['spinner_shown'] = True
                metrics['progressive_loading'] = True
            except TimeoutException:
                metrics['spinner_shown'] = False
                metrics['progressive_loading'] = False
                
        except Exception as e:
            metrics['spinner_shown'] = False
            metrics['progressive_loading'] = False
        
        return metrics
    
    def test_malformed_inputs_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Test form validation with malformed inputs in wizard"""
        metrics = {}
        
        # Open wizard
        create_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "createTaskBtn"))
        )
        
        modal_start = time.time()
        create_btn.click()
        
        # Wait for modal
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "step1"))
        )
        
        modal_end = time.time()
        metrics['modal_load_ms'] = (modal_end - modal_start) * 1000
        
        # Leave title empty and try to proceed
        next_btn = self.driver.find_element(By.ID, "nextBtn")
        next_btn.click()
        
        time.sleep(1)  # Allow for validation
        
        # Check for validation errors
        error_groups = self.driver.find_elements(By.CLASS_NAME, "error")
        metrics['validation_errors_shown'] = len(error_groups) > 0
        
        error_messages = self.driver.find_elements(By.CLASS_NAME, "error-message")
        metrics['form_submission_blocked'] = len(error_messages) > 0
        
        # Check if we're still on step 1 (validation blocked progression)
        step1_active = self.driver.find_element(By.ID, "step1").get_attribute("class")
        metrics['form_submission_blocked'] = "active" in step1_active
        
        # Check error message accessibility
        metrics['error_messages_accessible'] = all(
            msg.is_displayed() and msg.text for msg in error_messages
        )
        
        # Check field highlighting
        highlighted_fields = self.driver.find_elements(By.CSS_SELECTOR, ".form-group.error input")
        metrics['field_highlighting'] = len(highlighted_fields) > 0
        
        # Accessibility score
        metrics['accessibility_score'] = self.calculate_accessibility_score()
        
        return metrics
    
    def test_accessibility_keyboard_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Test keyboard navigation and accessibility in wizard"""
        metrics = {}
        
        # Open wizard using keyboard
        create_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "createTaskBtn"))
        )
        
        modal_start = time.time()
        
        # Focus and activate with keyboard
        actions = ActionChains(self.driver)
        actions.click(create_btn).perform()
        
        # Wait for wizard
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "step1"))
        )
        
        modal_end = time.time()
        metrics['modal_load_ms'] = (modal_end - modal_start) * 1000
        
        # Test keyboard navigation
        focusable_elements = self.driver.find_elements(
            By.CSS_SELECTOR, 
            "input:not([type='hidden']), select, textarea, button:not(:disabled)"
        )
        
        metrics['keyboard_navigation_functional'] = len(focusable_elements) > 0
        
        # Test tab order
        tab_order_logical = True
        try:
            # Start with first focusable element
            if focusable_elements:
                focusable_elements[0].click()
                
                # Tab through several elements
                for i in range(min(3, len(focusable_elements) - 1)):
                    actions.send_keys("\t")
                    time.sleep(0.1)
                    
        except Exception:
            tab_order_logical = False
        
        metrics['tab_order_logical'] = tab_order_logical
        
        # Check ARIA labels and attributes
        aria_elements = self.driver.find_elements(By.CSS_SELECTOR, 
            "[aria-label], [aria-labelledby], [aria-describedby], [role]")
        metrics['aria_labels_present'] = len(aria_elements) > 0
        
        # Check focus indicators
        try:
            focused_element = self.driver.switch_to.active_element
            focus_outline = focused_element.value_of_css_property('outline')
            metrics['focus_indicators_visible'] = (
                focus_outline and focus_outline != 'none' and 
                focus_outline != 'rgb(0, 0, 0) none 0px'
            )
        except Exception:
            metrics['focus_indicators_visible'] = False
        
        # Check for proper heading structure
        headings = self.driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6")
        labels = self.driver.find_elements(By.TAG_NAME, "label")
        metrics['screen_reader_compatible'] = len(headings) > 0 and len(labels) > 0
        
        # Overall accessibility score (should be higher for improved version)
        metrics['accessibility_score'] = self.calculate_accessibility_score()
        
        return metrics
    
    def calculate_accessibility_score(self) -> float:
        """Calculate enhanced accessibility score"""
        score = 0.0
        checks = 0
        
        # Check for labels
        try:
            labels = self.driver.find_elements(By.TAG_NAME, "label")
            inputs = self.driver.find_elements(By.CSS_SELECTOR, "input, select, textarea")
            if len(labels) > 0 and len(inputs) > 0:
                score += 0.15
            checks += 1
        except Exception:
            checks += 1
        
        # Check for headings
        try:
            headings = self.driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6")
            if len(headings) > 0:
                score += 0.15
            checks += 1
        except Exception:
            checks += 1
        
        # Check for ARIA attributes (enhanced)
        try:
            aria_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                "[aria-label], [aria-labelledby], [aria-describedby], [role]")
            if len(aria_elements) > 3:  # Higher threshold for improved version
                score += 0.2
            checks += 1
        except Exception:
            checks += 1
        
        # Check for help text
        try:
            help_elements = self.driver.find_elements(By.CLASS_NAME, "help-text")
            if len(help_elements) > 0:
                score += 0.15
            checks += 1
        except Exception:
            checks += 1
        
        # Check for required field indicators
        try:
            required_indicators = self.driver.find_elements(By.CLASS_NAME, "required")
            if len(required_indicators) > 0:
                score += 0.15
            checks += 1
        except Exception:
            checks += 1
        
        # Check for focus management (improved version specific)
        try:
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            if any("focus" in btn.get_attribute("style") or "" for btn in buttons):
                score += 0.1
            checks += 1
        except Exception:
            checks += 1
        
        # Check for semantic structure
        try:
            sections = self.driver.find_elements(By.CSS_SELECTOR, "section, main, article")
            if len(sections) > 0:
                score += 0.1
            checks += 1
        except Exception:
            checks += 1
        
        return score if checks == 0 else score
    
    def take_screenshot(self, name: str) -> str:
        """Take a screenshot and return the path"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots_post_{name}_{timestamp}.png"
        filepath = self.screenshots_dir / filename
        
        if self.driver:
            self.driver.save_screenshot(str(filepath))
        
        return str(filepath)
    
    def run_all_tests(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run all test cases"""
        print("Starting Post-improvement UI tests...")
        
        if not self.start_server():
            return {'error': 'Failed to start server'}
        
        try:
            all_results = {
                'project': 'Project_B_PostImprove_UI',
                'version': 'post-improvement',
                'timestamp': datetime.now().isoformat(),
                'test_results': []
            }
            
            test_cases = test_data['test_cases']
            
            for test_case in test_cases:
                result = self.run_test_case(test_case)
                all_results['test_results'].append(result)
                self.results.append(result)
            
            # Save results
            results_file = self.results_dir / 'results_post.json'
            with open(results_file, 'w') as f:
                json.dump(all_results, f, indent=2, default=str)
            
            print(f"\nTests completed. Results saved to {results_file}")
            return all_results
            
        finally:
            self.stop_server()

def main():
    """Main test execution function"""
    # Load test data
    test_data_path = Path(__file__).parent.parent / 'data' / 'test_data.json'
    
    if not test_data_path.exists():
        # Fallback to shared test data
        test_data_path = Path(__file__).parent.parent.parent / 'test_data.json'
    
    if not test_data_path.exists():
        print(f"Test data file not found: {test_data_path}")
        sys.exit(1)
    
    with open(test_data_path, 'r') as f:
        test_data = json.load(f)
    
    # Configuration
    config = {
        'server_port': 8002,
        'headless': os.getenv('HEADLESS', 'false').lower() == 'true',
        'repeat_count': int(os.getenv('REPEAT_COUNT', '1')),
        'network_latency': int(os.getenv('NETWORK_LATENCY', '100'))
    }
    
    # Initialize tester
    tester = PostImprovementUITester(config)
    
    # Run tests
    results = tester.run_all_tests(test_data)
    
    if 'error' in results:
        print(f"Test execution failed: {results['error']}")
        sys.exit(1)
    
    # Print summary
    print("\n" + "="*50)
    print("TEST SUMMARY - Post-improvement UI")
    print("="*50)
    
    passed = sum(1 for r in results['test_results'] if r['status'] == 'passed')
    failed = sum(1 for r in results['test_results'] if r['status'] == 'failed')
    total = len(results['test_results'])
    
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()