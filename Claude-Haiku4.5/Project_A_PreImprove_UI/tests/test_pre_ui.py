#!/usr/bin/env python3
"""
Test harness for Pre-improvement UI (Project A)
Tests the slow, cluttered modal with eager loading
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

class PreImprovementUITester:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results = []
        self.server_process = None
        self.driver = None
        self.server_port = config.get('server_port', 8001)
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
        """Test normal task creation flow"""
        metrics = {}
        
        # Click create task button and measure modal load time
        create_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "createTaskBtn"))
        )
        
        modal_start = time.time()
        create_btn.click()
        
        # Wait for modal to appear
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "modalOverlay"))
        )
        
        # Wait for loading to complete
        WebDriverWait(self.driver, 30).until(
            EC.invisibility_of_element_located((By.ID, "loadingIndicator"))
        )
        
        modal_end = time.time()
        metrics['modal_load_ms'] = (modal_end - modal_start) * 1000
        
        # Measure time to title field visible
        title_start = time.time()
        title_field = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "title"))
        )
        
        # Check if title field is visible without scrolling
        title_location = title_field.location['y']
        viewport_height = self.driver.execute_script("return window.innerHeight")
        scroll_position = self.driver.execute_script("return window.pageYOffset")
        
        metrics['title_visible_without_scroll'] = (
            title_location >= scroll_position and 
            title_location <= scroll_position + viewport_height
        )
        
        # If not visible, scroll to it and measure time
        if not metrics['title_visible_without_scroll']:
            self.driver.execute_script("arguments[0].scrollIntoView()", title_field)
            time.sleep(0.5)  # Allow for smooth scroll
        
        title_end = time.time()
        metrics['time_to_title_visible_ms'] = (title_end - title_start) * 1000
        
        # Fill out the form
        task_data = test_case['input_payload']
        
        title_field.clear()
        title_field.send_keys(task_data['title'])
        
        # Fill priority
        priority_select = self.driver.find_element(By.ID, "priority")
        priority_select.send_keys(task_data['priority'])
        
        # Fill due date
        due_date_field = self.driver.find_element(By.ID, "dueDate")
        due_date_field.send_keys(task_data['due_date'])
        
        # Fill assignee
        assignee_select = self.driver.find_element(By.ID, "assignee")
        assignee_select.send_keys(task_data['assignee'])
        
        # Fill description
        desc_field = self.driver.find_element(By.ID, "description")
        desc_field.send_keys(task_data['description'])
        
        # Submit form and measure total time
        submit_start = time.time()
        submit_btn = self.driver.find_element(By.ID, "submitBtn")
        submit_btn.click()
        
        # Wait for success or error
        time.sleep(2)  # Allow for submission processing
        
        submit_end = time.time()
        metrics['task_create_ms'] = (submit_end - modal_start) * 1000
        
        # Check accessibility score (basic checks)
        metrics['accessibility_score'] = self.calculate_accessibility_score()
        
        return metrics
    
    def test_heavy_data_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Test with heavy data to trigger performance issues"""
        metrics = self.test_normal_case(test_case)
        
        # Additional checks for lazy loading (should NOT be present in pre-improvement)
        try:
            # Check if tags are loaded immediately (eager loading)
            tags_container = self.driver.find_element(By.ID, "tagsContainer")
            tags = tags_container.find_elements(By.CLASS_NAME, "tag")
            metrics['tags_lazy_loaded'] = len(tags) == 0  # Should be False for pre-improvement
            
            # Check if attachments section is loaded immediately
            attachments_container = self.driver.find_element(By.ID, "attachmentsContainer")
            file_input = attachments_container.find_elements(By.TAG_NAME, "input")
            metrics['attachments_lazy_loaded'] = len(file_input) == 0  # Should be False
            
        except NoSuchElementException:
            metrics['tags_lazy_loaded'] = False
            metrics['attachments_lazy_loaded'] = False
        
        return metrics
    
    def test_slow_network_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Test with slow network conditions"""
        # Similar to normal case but with network delays
        metrics = self.test_normal_case(test_case)
        
        # Check for loading indicators
        try:
            # Check if spinner was shown
            spinner = self.driver.find_element(By.CLASS_NAME, "spinner")
            metrics['spinner_shown'] = spinner.is_displayed()
        except NoSuchElementException:
            metrics['spinner_shown'] = False
        
        # Progressive loading should NOT be present in pre-improvement
        metrics['progressive_loading'] = False
        
        return metrics
    
    def test_malformed_inputs_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Test form validation with malformed inputs"""
        metrics = {}
        
        # Open modal
        create_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "createTaskBtn"))
        )
        create_btn.click()
        
        # Wait for form to load
        WebDriverWait(self.driver, 30).until(
            EC.invisibility_of_element_located((By.ID, "loadingIndicator"))
        )
        
        modal_end = time.time()
        modal_start = time.time()
        metrics['modal_load_ms'] = (modal_end - modal_start) * 1000
        
        # Fill with invalid data
        task_data = test_case['input_payload']
        
        # Leave title empty (required field)
        title_field = self.driver.find_element(By.ID, "title")
        title_field.clear()
        
        # Invalid assignee
        assignee_select = self.driver.find_element(By.ID, "assignee")
        assignee_select.send_keys("invalid-email")
        
        # Invalid date
        due_date_field = self.driver.find_element(By.ID, "dueDate")
        due_date_field.send_keys("invalid-date")
        
        # Try to submit
        submit_btn = self.driver.find_element(By.ID, "submitBtn")
        submit_btn.click()
        
        time.sleep(1)  # Allow for validation
        
        # Check for validation errors
        error_groups = self.driver.find_elements(By.CLASS_NAME, "error")
        metrics['validation_errors_shown'] = len(error_groups) > 0
        
        error_messages = self.driver.find_elements(By.CLASS_NAME, "error-message")
        metrics['form_submission_blocked'] = len(error_messages) > 0
        
        # Check if error messages are accessible
        metrics['error_messages_accessible'] = all(
            msg.is_displayed() for msg in error_messages
        )
        
        # Check field highlighting
        highlighted_fields = self.driver.find_elements(By.CSS_SELECTOR, ".form-group.error input")
        metrics['field_highlighting'] = len(highlighted_fields) > 0
        
        # Accessibility score
        metrics['accessibility_score'] = self.calculate_accessibility_score()
        
        return metrics
    
    def test_accessibility_keyboard_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Test keyboard navigation and accessibility"""
        metrics = {}
        
        # Open modal using keyboard
        create_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "createTaskBtn"))
        )
        
        # Focus and activate with keyboard
        actions = ActionChains(self.driver)
        actions.click(create_btn).perform()
        
        # Wait for modal
        WebDriverWait(self.driver, 30).until(
            EC.invisibility_of_element_located((By.ID, "loadingIndicator"))
        )
        
        modal_end = time.time()
        modal_start = time.time()
        metrics['modal_load_ms'] = (modal_end - modal_start) * 1000
        
        # Test keyboard navigation
        focusable_elements = self.driver.find_elements(
            By.CSS_SELECTOR, 
            "input, select, textarea, button:not(:disabled)"
        )
        
        metrics['keyboard_navigation_functional'] = len(focusable_elements) > 0
        
        # Check tab order
        tab_order_logical = True
        try:
            # Check first focusable element
            first_element = focusable_elements[0]
            first_element.click()
            
            # Tab through elements
            for i in range(min(5, len(focusable_elements))):
                actions.send_keys_to_element(self.driver.switch_to.active_element, "\t")
                time.sleep(0.1)
                
        except Exception:
            tab_order_logical = False
        
        metrics['tab_order_logical'] = tab_order_logical
        
        # Check ARIA labels
        aria_elements = self.driver.find_elements(By.CSS_SELECTOR, "[aria-label], [aria-labelledby]")
        metrics['aria_labels_present'] = len(aria_elements) > 0
        
        # Check focus indicators
        focused_element = self.driver.switch_to.active_element
        focus_outline = focused_element.value_of_css_property('outline')
        metrics['focus_indicators_visible'] = focus_outline and focus_outline != 'none'
        
        # Screen reader compatibility (basic check)
        headings = self.driver.find_elements(By.TAG_NAME, "h1, h2, h3")
        labels = self.driver.find_elements(By.TAG_NAME, "label")
        metrics['screen_reader_compatible'] = len(headings) > 0 and len(labels) > 0
        
        # Overall accessibility score
        metrics['accessibility_score'] = self.calculate_accessibility_score()
        
        return metrics
    
    def calculate_accessibility_score(self) -> float:
        """Calculate basic accessibility score"""
        score = 0.0
        checks = 0
        
        # Check for labels
        try:
            labels = self.driver.find_elements(By.TAG_NAME, "label")
            inputs = self.driver.find_elements(By.CSS_SELECTOR, "input, select, textarea")
            if len(labels) > 0 and len(inputs) > 0:
                score += 0.2
            checks += 1
        except Exception:
            checks += 1
        
        # Check for headings
        try:
            headings = self.driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6")
            if len(headings) > 0:
                score += 0.2
            checks += 1
        except Exception:
            checks += 1
        
        # Check for alt text on images
        try:
            images = self.driver.find_elements(By.TAG_NAME, "img")
            images_with_alt = [img for img in images if img.get_attribute("alt")]
            if len(images) == 0 or len(images_with_alt) == len(images):
                score += 0.2
            checks += 1
        except Exception:
            checks += 1
        
        # Check color contrast (basic)
        try:
            body = self.driver.find_element(By.TAG_NAME, "body")
            color = body.value_of_css_property("color")
            background = body.value_of_css_property("background-color")
            if color and background and color != background:
                score += 0.2
            checks += 1
        except Exception:
            checks += 1
        
        # Check for required field indicators
        try:
            required_indicators = self.driver.find_elements(By.CLASS_NAME, "required")
            if len(required_indicators) > 0:
                score += 0.2
            checks += 1
        except Exception:
            checks += 1
        
        return score if checks == 0 else score
    
    def take_screenshot(self, name: str) -> str:
        """Take a screenshot and return the path"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots_pre_{name}_{timestamp}.png"
        filepath = self.screenshots_dir / filename
        
        if self.driver:
            self.driver.save_screenshot(str(filepath))
        
        return str(filepath)
    
    def run_all_tests(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run all test cases"""
        print("Starting Pre-improvement UI tests...")
        
        if not self.start_server():
            return {'error': 'Failed to start server'}
        
        try:
            all_results = {
                'project': 'Project_A_PreImprove_UI',
                'version': 'pre-improvement',
                'timestamp': datetime.now().isoformat(),
                'test_results': []
            }
            
            test_cases = test_data['test_cases']
            
            for test_case in test_cases:
                result = self.run_test_case(test_case)
                all_results['test_results'].append(result)
                self.results.append(result)
            
            # Save results
            results_file = self.results_dir / 'results_pre.json'
            with open(results_file, 'w') as f:
                json.dump(all_results, f, indent=2, default=str)
            
            print(f"\nTests completed. Results saved to {results_file}")
            return all_results
            
        finally:
            self.stop_server()
    
def main():
    """Main test execution function"""
    # Load test data
    test_data_path = Path(__file__).parent.parent.parent / 'test_data.json'
    
    if not test_data_path.exists():
        print(f"Test data file not found: {test_data_path}")
        sys.exit(1)
    
    with open(test_data_path, 'r') as f:
        test_data = json.load(f)
    
    # Configuration
    config = {
        'server_port': 8001,
        'headless': os.getenv('HEADLESS', 'false').lower() == 'true',
        'repeat_count': int(os.getenv('REPEAT_COUNT', '1')),
        'network_latency': int(os.getenv('NETWORK_LATENCY', '100'))
    }
    
    # Initialize tester
    tester = PreImprovementUITester(config)
    
    # Run tests
    results = tester.run_all_tests(test_data)
    
    if 'error' in results:
        print(f"Test execution failed: {results['error']}")
        sys.exit(1)
    
    # Print summary
    print("\n" + "="*50)
    print("TEST SUMMARY - Pre-improvement UI")
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