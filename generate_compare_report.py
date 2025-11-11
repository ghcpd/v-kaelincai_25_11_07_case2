#!/usr/bin/env python3
"""
Generate comparison report comparing pre-improvement and post-improvement results.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

def load_json(path):
    """Load JSON file"""
    with open(path, 'r') as f:
        return json.load(f)

def calculate_improvement(before, after):
    """Calculate percentage improvement"""
    if before == 0:
        return 0
    return round(((before - after) / before) * 100, 2)

def format_ms(ms):
    """Format milliseconds"""
    return f"{ms:.2f}ms"

def generate_report(pre_results_path, post_results_path, test_data_path, output_path):
    """Generate comparison report"""
    
    # Load data
    pre_results = load_json(pre_results_path)
    post_results = load_json(post_results_path)
    test_data = load_json(test_data_path)
    
    # Extract summaries
    pre_summary = pre_results.get('summary', {})
    post_summary = post_results.get('summary', {})
    
    # Extract individual test results
    pre_test_results = {r['test_id']: r for r in pre_results.get('results', [])}
    post_test_results = {r['test_id']: r for r in post_results.get('results', [])}
    
    # Generate markdown report
    report = []
    report.append("# UI/UX Improvement Comparison Report")
    report.append("")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    report.append("---")
    report.append("")
    
    # Executive Summary
    report.append("## Executive Summary")
    report.append("")
    
    # Overall metrics comparison
    pre_modal_avg = pre_summary.get('avg_modal_load_ms', 0)
    post_modal_avg = post_summary.get('avg_modal_load_ms', 0)
    modal_improvement = calculate_improvement(pre_modal_avg, post_modal_avg)
    
    pre_task_avg = pre_summary.get('avg_task_create_ms', 0)
    post_task_avg = post_summary.get('avg_task_create_ms', 0)
    task_improvement = calculate_improvement(pre_task_avg, post_task_avg)
    
    pre_success_rate = pre_summary.get('success_rate', 0)
    post_success_rate = post_summary.get('success_rate', 0)
    
    post_visibility_rate = post_summary.get('first_field_visibility_rate', 0)
    
    report.append("### Key Improvements")
    report.append("")
    report.append(f"- **Modal Load Time:** {format_ms(pre_modal_avg)} → {format_ms(post_modal_avg)} ({modal_improvement:+}%)")
    report.append(f"- **Task Creation Time:** {format_ms(pre_task_avg)} → {format_ms(post_task_avg)} ({task_improvement:+}%)")
    report.append(f"- **Test Success Rate:** {pre_success_rate}% → {post_success_rate}%")
    report.append(f"- **First Field Visibility Rate:** {post_visibility_rate}% (Post-Improvement)")
    report.append("")
    
    # Improvement thresholds
    report.append("### Improvement Thresholds")
    report.append("")
    report.append("- Modal load time reduction: **≥30%** ✅" if modal_improvement >= 30 else "- Modal load time reduction: **≥30%** ❌")
    report.append("- Task creation time reduction: **≥20%** ✅" if task_improvement >= 20 else "- Task creation time reduction: **≥20%** ❌")
    report.append("- First field visibility: **≥95%** ✅" if post_visibility_rate >= 95 else "- First field visibility: **≥95%** ❌")
    report.append("")
    
    # Per-Case Comparison
    report.append("## Per-Case Comparison")
    report.append("")
    
    test_cases = test_data.get('test_cases', [])
    
    for test_case in test_cases:
        test_id = test_case['id']
        report.append(f"### Test Case: {test_id}")
        report.append("")
        report.append(f"**Description:** {test_case.get('description', 'N/A')}")
        report.append("")
        
        pre_result = pre_test_results.get(test_id, {})
        post_result = post_test_results.get(test_id, {})
        
        pre_metrics = pre_result.get('metrics', {})
        post_metrics = post_result.get('metrics', {})
        
        # Metrics comparison table
        report.append("| Metric | Pre-Improvement | Post-Improvement | Improvement |")
        report.append("|--------|----------------|------------------|-------------|")
        
        # Modal load time
        pre_modal = pre_metrics.get('modal_load_ms', 0)
        post_modal = post_metrics.get('modal_load_ms', 0)
        if pre_modal and post_modal:
            modal_imp = calculate_improvement(pre_modal, post_modal)
            report.append(f"| Modal Load Time | {format_ms(pre_modal)} | {format_ms(post_modal)} | {modal_imp:+}% |")
        
        # Time to title visible
        pre_title = pre_metrics.get('time_to_title_visible_ms', 0)
        post_title = post_metrics.get('time_to_title_visible_ms', 0)
        if pre_title and post_title:
            title_imp = calculate_improvement(pre_title, post_title)
            report.append(f"| Time to Title Visible | {format_ms(pre_title)} | {format_ms(post_title)} | {title_imp:+}% |")
        
        # Task creation time
        pre_task = pre_metrics.get('task_create_ms', 0)
        post_task = post_metrics.get('task_create_ms', 0)
        if pre_task and post_task:
            task_imp = calculate_improvement(pre_task, post_task)
            report.append(f"| Task Creation Time | {format_ms(pre_task)} | {format_ms(post_task)} | {task_imp:+}% |")
        
        # First field visibility
        pre_visible = pre_metrics.get('first_field_visible', False)
        post_visible = post_metrics.get('first_field_visible', False)
        report.append(f"| First Field Visible | {'✅' if pre_visible else '❌'} | {'✅' if post_visible else '❌'} | {'✅ Improved' if not pre_visible and post_visible else '—'} |")
        
        report.append("")
        
        # Pass/Fail status
        pre_passed = pre_result.get('passed', False)
        post_passed = post_result.get('passed', False)
        
        report.append(f"**Status:** Pre: {'✅ PASS' if pre_passed else '❌ FAIL'} | Post: {'✅ PASS' if post_passed else '❌ FAIL'}")
        report.append("")
        
        # Screenshots
        pre_screenshot = pre_result.get('screenshot', '')
        post_screenshot = post_result.get('screenshot', '')
        
        if pre_screenshot or post_screenshot:
            report.append("**Screenshots:**")
            report.append("")
            if pre_screenshot:
                report.append(f"- Pre-Improvement: `{pre_screenshot}`")
            if post_screenshot:
                report.append(f"- Post-Improvement: `{post_screenshot}`")
            report.append("")
        
        # Errors
        pre_errors = pre_result.get('errors', [])
        post_errors = post_result.get('errors', [])
        
        if pre_errors:
            report.append("**Pre-Improvement Errors:**")
            for error in pre_errors[:3]:  # Show first 3 errors
                report.append(f"- {error[:100]}...")
            report.append("")
        
        if post_errors:
            report.append("**Post-Improvement Errors:**")
            for error in post_errors[:3]:
                report.append(f"- {error[:100]}...")
            report.append("")
        
        report.append("---")
        report.append("")
    
    # Detailed Metrics
    report.append("## Detailed Metrics Summary")
    report.append("")
    
    report.append("### Pre-Improvement Summary")
    report.append("")
    report.append(f"- Total Tests: {pre_summary.get('total_tests', 0)}")
    report.append(f"- Passed: {pre_summary.get('passed_tests', 0)}")
    report.append(f"- Failed: {pre_summary.get('failed_tests', 0)}")
    report.append(f"- Success Rate: {pre_summary.get('success_rate', 0)}%")
    report.append(f"- Average Modal Load Time: {format_ms(pre_summary.get('avg_modal_load_ms', 0))}")
    report.append(f"- Median Modal Load Time: {format_ms(pre_summary.get('median_modal_load_ms', 0))}")
    report.append(f"- Average Task Creation Time: {format_ms(pre_summary.get('avg_task_create_ms', 0))}")
    report.append(f"- Median Task Creation Time: {format_ms(pre_summary.get('median_task_create_ms', 0))}")
    report.append("")
    
    report.append("### Post-Improvement Summary")
    report.append("")
    report.append(f"- Total Tests: {post_summary.get('total_tests', 0)}")
    report.append(f"- Passed: {post_summary.get('passed_tests', 0)}")
    report.append(f"- Failed: {post_summary.get('failed_tests', 0)}")
    report.append(f"- Success Rate: {post_summary.get('success_rate', 0)}%")
    report.append(f"- Average Modal Load Time: {format_ms(post_summary.get('avg_modal_load_ms', 0))}")
    report.append(f"- Median Modal Load Time: {format_ms(post_summary.get('median_modal_load_ms', 0))}")
    report.append(f"- Average Task Creation Time: {format_ms(post_summary.get('avg_task_create_ms', 0))}")
    report.append(f"- Median Task Creation Time: {format_ms(post_summary.get('median_task_create_ms', 0))}")
    report.append(f"- First Field Visibility Rate: {post_summary.get('first_field_visibility_rate', 0)}%")
    report.append("")
    
    # Recommendations
    report.append("## Recommendations")
    report.append("")
    report.append("### Rollout Strategy")
    report.append("")
    report.append("1. **A/B Testing:** Deploy the wizard UI to a subset of users (10-20%) and monitor:")
    report.append("   - Task creation completion rates")
    report.append("   - User feedback and satisfaction scores")
    report.append("   - Performance metrics in production")
    report.append("")
    report.append("2. **Progressive Rollout:** Gradually increase the percentage of users on the new UI:")
    report.append("   - Week 1: 10% of users")
    report.append("   - Week 2: 25% of users")
    report.append("   - Week 3: 50% of users")
    report.append("   - Week 4: 100% of users")
    report.append("")
    report.append("3. **Telemetry & Monitoring:**")
    report.append("   - Track modal open times in production")
    report.append("   - Monitor task creation success rates")
    report.append("   - Collect user interaction analytics")
    report.append("   - Set up alerts for performance regressions")
    report.append("")
    
    report.append("### Accessibility Improvements")
    report.append("")
    report.append("The post-improvement version includes:")
    report.append("- ARIA labels and roles for screen readers")
    report.append("- Keyboard navigation support")
    report.append("- Focus indicators")
    report.append("- Semantic HTML structure")
    report.append("")
    report.append("**Additional Recommendations:**")
    report.append("- Conduct user testing with screen reader users")
    report.append("- Add skip links for keyboard navigation")
    report.append("- Ensure color contrast meets WCAG AA standards")
    report.append("- Provide alternative text for icons and images")
    report.append("")
    
    # Limitations
    report.append("## Limitations & Notes")
    report.append("")
    report.append("### Testing Limitations")
    report.append("")
    report.append("- **Browser Differences:** Tests run in Chromium; results may vary in Firefox/Safari")
    report.append("- **Network Simulation:** Simulated network delays may not reflect real-world conditions")
    report.append("- **Device Emulation:** Tests don't account for mobile device performance")
    report.append("- **User Behavior:** Automated tests don't capture real user interaction patterns")
    report.append("")
    report.append("### Known Issues")
    report.append("")
    report.append("- Network delay simulation may not perfectly match real-world latency")
    report.append("- Screenshots are captured at specific moments and may not show all states")
    report.append("- Test timing may vary based on system load")
    report.append("")
    
    # Write report
    with open(output_path, 'w') as f:
        f.write('\n'.join(report))
    
    print(f"Comparison report generated: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Generate comparison report')
    parser.add_argument('--pre-results', default='Project_A_PreImprove_UI/results/results_pre.json', help='Pre-improvement results JSON')
    parser.add_argument('--post-results', default='Project_B_PostImprove_UI/results/results_post.json', help='Post-improvement results JSON')
    parser.add_argument('--test-data', default='test_data.json', help='Test data JSON')
    parser.add_argument('--output', default='compare_report.md', help='Output markdown file')
    args = parser.parse_args()
    
    generate_report(
        args.pre_results,
        args.post_results,
        args.test_data,
        args.output
    )

if __name__ == '__main__':
    main()

