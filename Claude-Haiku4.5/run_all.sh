#!/bin/bash
# Master script to run both projects and generate comparison report
# Usage: ./run_all.sh [repeat_count] [network_latency_ms] [headless]

set -e  # Exit on any error

echo "======================================================="
echo "UI/UX Improvement Evaluation - Complete Test Suite"
echo "======================================================="
echo ""

# Configuration
REPEAT_COUNT=${1:-1}
NETWORK_LATENCY=${2:-100}
HEADLESS=${3:-false}

echo "Configuration:"
echo "  Repeat count: $REPEAT_COUNT"
echo "  Network latency: ${NETWORK_LATENCY}ms"
echo "  Headless mode: $HEADLESS"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
WORKSPACE_ROOT="$SCRIPT_DIR"

# Create results directory if it doesn't exist
mkdir -p "$WORKSPACE_ROOT/results"

# Track execution start time
EXECUTION_START=$(date +%s)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "Starting execution at: $(date)"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "Checking dependencies..."
if ! command_exists python; then
    echo "Error: Python is not installed or not in PATH"
    exit 1
fi

if ! command_exists pip; then
    echo "Error: pip is not installed or not in PATH"
    exit 1
fi

echo "✓ Python and pip are available"
echo ""

# Function to run a project
run_project() {
    local project_name="$1"
    local project_dir="$2"
    
    echo "========================================"
    echo "Running $project_name"
    echo "========================================"
    
    if [ ! -d "$project_dir" ]; then
        echo "Error: Project directory not found: $project_dir"
        return 1
    fi
    
    cd "$project_dir"
    
    # Check if setup is needed
    if [ ! -d "venv" ]; then
        echo "Setting up $project_name environment..."
        if [ -f "setup.sh" ]; then
            bash setup.sh
        else
            echo "Warning: setup.sh not found, attempting to create venv..."
            python -m venv venv
            
            # Activate and install requirements
            if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
                source venv/Scripts/activate
            else
                source venv/bin/activate
            fi
            
            if [ -f "requirements.txt" ]; then
                pip install -r requirements.txt
            fi
        fi
    fi
    
    # Run tests
    echo ""
    echo "Executing tests for $project_name..."
    if [ -f "run_tests.sh" ]; then
        bash run_tests.sh "$REPEAT_COUNT" "$NETWORK_LATENCY" "$HEADLESS"
    else
        echo "Error: run_tests.sh not found in $project_dir"
        return 1
    fi
    
    cd "$WORKSPACE_ROOT"
    echo ""
    echo "$project_name tests completed"
    echo ""
}

# Initialize execution log
EXECUTION_LOG="$WORKSPACE_ROOT/results/execution_log_${TIMESTAMP}.txt"
exec > >(tee -a "$EXECUTION_LOG") 2>&1

# Run Project A - Pre-improvement
echo "Phase 1: Pre-improvement Testing"
echo "================================="
if ! run_project "Project A (Pre-improvement)" "$WORKSPACE_ROOT/Project_A_PreImprove_UI"; then
    echo "❌ Project A failed. Continuing with Project B..."
fi

echo ""
echo "Phase 2: Post-improvement Testing"
echo "=================================="
if ! run_project "Project B (Post-improvement)" "$WORKSPACE_ROOT/Project_B_PostImprove_UI"; then
    echo "❌ Project B failed. Generating partial comparison..."
fi

# Generate comparison report
echo ""
echo "Phase 3: Generating Comparison Report"
echo "====================================="

# Create comparison script
cat > "$WORKSPACE_ROOT/generate_comparison.py" << 'EOF'
#!/usr/bin/env python3
"""
Generate comparison report between pre and post improvement results
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

def load_results(project_dir: str, result_type: str) -> Optional[Dict[str, Any]]:
    """Load test results from a project directory"""
    results_dir = Path(project_dir) / 'results'
    
    # Look for the most recent results file
    pattern = f'results_{result_type}*.json'
    result_files = list(results_dir.glob(pattern))
    
    if not result_files:
        print(f"Warning: No {result_type} results found in {results_dir}")
        return None
    
    # Use the most recent file
    latest_file = max(result_files, key=lambda f: f.stat().st_mtime)
    
    try:
        with open(latest_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {latest_file}: {e}")
        return None

def calculate_improvement(pre_value: float, post_value: float) -> Dict[str, Any]:
    """Calculate improvement metrics"""
    if pre_value == 0:
        return {
            'absolute_change': post_value,
            'percent_change': float('inf') if post_value > 0 else 0,
            'improvement': post_value < pre_value
        }
    
    absolute_change = post_value - pre_value
    percent_change = (absolute_change / pre_value) * 100
    improvement = post_value < pre_value  # Lower is better for timing metrics
    
    return {
        'absolute_change': absolute_change,
        'percent_change': percent_change,
        'improvement': improvement
    }

def format_metric(value: Any) -> str:
    """Format a metric value for display"""
    if isinstance(value, bool):
        return "✓" if value else "✗"
    elif isinstance(value, (int, float)):
        if value < 1:
            return f"{value:.3f}"
        elif value < 1000:
            return f"{value:.1f}"
        else:
            return f"{value:,.0f}"
    else:
        return str(value)

def generate_markdown_report(pre_results: Optional[Dict], post_results: Optional[Dict]) -> str:
    """Generate a comprehensive markdown comparison report"""
    
    report_lines = [
        "# UI/UX Improvement Evaluation Report",
        "",
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Executive Summary",
        ""
    ]
    
    if not pre_results and not post_results:
        report_lines.extend([
            "⚠️ **No test results found for either project.**",
            "",
            "Please ensure both projects have been executed successfully before generating the comparison report.",
            ""
        ])
        return "\n".join(report_lines)
    
    if not pre_results:
        report_lines.extend([
            "⚠️ **Pre-improvement results not found.**",
            "",
            "Only post-improvement results are available. Run Project A to get complete comparison.",
            ""
        ])
    elif not post_results:
        report_lines.extend([
            "⚠️ **Post-improvement results not found.**",
            "",
            "Only pre-improvement results are available. Run Project B to get complete comparison.",
            ""
        ])
    else:
        # Full comparison available
        report_lines.extend([
            "✅ **Complete comparison data available**",
            "",
            "Both pre-improvement and post-improvement test results were successfully collected and analyzed.",
            ""
        ])
    
    # Test Results Summary
    report_lines.extend([
        "## Test Execution Summary",
        "",
        "| Project | Status | Test Cases | Passed | Failed | Success Rate |",
        "|---------|--------|------------|--------|--------|--------------|"
    ])
    
    if pre_results:
        pre_test_results = pre_results.get('test_results', [])
        pre_passed = sum(1 for r in pre_test_results if r.get('status') == 'passed')
        pre_failed = sum(1 for r in pre_test_results if r.get('status') == 'failed')
        pre_total = len(pre_test_results)
        pre_success_rate = (pre_passed / pre_total * 100) if pre_total > 0 else 0
        
        report_lines.append(f"| Pre-improvement | {'✅' if pre_failed == 0 else '❌'} | {pre_total} | {pre_passed} | {pre_failed} | {pre_success_rate:.1f}% |")
    
    if post_results:
        post_test_results = post_results.get('test_results', [])
        post_passed = sum(1 for r in post_test_results if r.get('status') == 'passed')
        post_failed = sum(1 for r in post_test_results if r.get('status') == 'failed')
        post_total = len(post_test_results)
        post_success_rate = (post_passed / post_total * 100) if post_total > 0 else 0
        
        report_lines.append(f"| Post-improvement | {'✅' if post_failed == 0 else '❌'} | {post_total} | {post_passed} | {post_failed} | {post_success_rate:.1f}% |")
    
    report_lines.extend(["", ""])
    
    # Performance Metrics Comparison
    if pre_results and post_results:
        report_lines.extend([
            "## Performance Metrics Comparison",
            "",
            "### Key Performance Indicators",
            "",
            "| Metric | Pre-improvement | Post-improvement | Change | Improvement |",
            "|--------|-----------------|------------------|--------|-------------|"
        ])
        
        # Aggregate metrics across all test cases
        pre_metrics = aggregate_metrics(pre_results.get('test_results', []))
        post_metrics = aggregate_metrics(post_results.get('test_results', []))
        
        key_metrics = [
            ('modal_load_ms', 'Modal Load Time (ms)'),
            ('time_to_title_visible_ms', 'Time to Title Visible (ms)'),
            ('task_create_ms', 'Task Creation Time (ms)'),
            ('accessibility_score', 'Accessibility Score')
        ]
        
        for metric_key, metric_label in key_metrics:
            if metric_key in pre_metrics and metric_key in post_metrics:
                pre_val = pre_metrics[metric_key]
                post_val = post_metrics[metric_key]
                
                if metric_key == 'accessibility_score':
                    # Higher is better for accessibility
                    improvement_calc = calculate_improvement(1-pre_val, 1-post_val)
                    improvement_calc['improvement'] = post_val > pre_val
                else:
                    # Lower is better for timing metrics
                    improvement_calc = calculate_improvement(pre_val, post_val)
                
                change_str = f"{improvement_calc['percent_change']:+.1f}%"
                improvement_indicator = "✅" if improvement_calc['improvement'] else "❌"
                
                report_lines.append(f"| {metric_label} | {format_metric(pre_val)} | {format_metric(post_val)} | {change_str} | {improvement_indicator} |")
        
        report_lines.extend(["", ""])
    
    # Detailed Test Case Results
    report_lines.extend([
        "## Detailed Test Case Results",
        ""
    ])
    
    if pre_results and post_results:
        test_cases = set()
        if pre_results.get('test_results'):
            test_cases.update(r.get('test_id', 'unknown') for r in pre_results['test_results'])
        if post_results.get('test_results'):
            test_cases.update(r.get('test_id', 'unknown') for r in post_results['test_results'])
        
        for test_id in sorted(test_cases):
            report_lines.extend(generate_test_case_comparison(test_id, pre_results, post_results))
    
    # Recommendations
    report_lines.extend([
        "## Recommendations",
        "",
        "### Production Rollout Strategy",
        "",
        "1. **A/B Testing**: Implement a gradual rollout with 10% traffic initially",
        "2. **Performance Monitoring**: Set up real-time monitoring for modal load times",
        "3. **User Feedback**: Collect user satisfaction metrics during rollout",
        "4. **Accessibility Validation**: Conduct comprehensive screen reader testing",
        "",
        "### Key Success Metrics to Monitor",
        "",
        "- Modal opening time < 150ms",
        "- Time to first input focus < 100ms", 
        "- Task creation completion rate > 95%",
        "- User satisfaction score improvement",
        "",
        "### Limitations and Considerations",
        "",
        "- Test results are based on automated browser testing",
        "- Real user performance may vary based on device and network conditions",
        "- Accessibility testing should be supplemented with actual user testing",
        "- Consider progressive enhancement for older browsers",
        "",
        "---",
        "",
        f"*Report generated by UI/UX Improvement Evaluation System on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    ])
    
    return "\n".join(report_lines)

def aggregate_metrics(test_results: List[Dict[str, Any]]) -> Dict[str, float]:
    """Aggregate metrics across all test results"""
    aggregated = {}
    
    for result in test_results:
        if result.get('status') != 'passed':
            continue
            
        metrics = result.get('metrics', {})
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                if key not in aggregated:
                    aggregated[key] = []
                aggregated[key].append(value)
    
    # Calculate averages
    return {key: sum(values) / len(values) for key, values in aggregated.items() if values}

def generate_test_case_comparison(test_id: str, pre_results: Dict, post_results: Dict) -> List[str]:
    """Generate comparison for a specific test case"""
    lines = [f"### {test_id.replace('_', ' ').title()}", ""]
    
    pre_test = None
    post_test = None
    
    # Find the test case in each set of results
    for test in pre_results.get('test_results', []):
        if test.get('test_id') == test_id:
            pre_test = test
            break
    
    for test in post_results.get('test_results', []):
        if test.get('test_id') == test_id:
            post_test = test
            break
    
    if not pre_test and not post_test:
        lines.extend(["*No results available for this test case.*", ""])
        return lines
    
    # Test description
    description = (pre_test or post_test).get('description', 'No description available')
    lines.extend([f"**Description**: {description}", ""])
    
    # Status comparison
    pre_status = pre_test.get('status', 'Not run') if pre_test else 'Not run'
    post_status = post_test.get('status', 'Not run') if post_test else 'Not run'
    
    lines.extend([
        f"**Status**: Pre: {pre_status} | Post: {post_status}",
        ""
    ])
    
    # Metrics comparison
    if pre_test and post_test and pre_status == 'passed' and post_status == 'passed':
        pre_metrics = pre_test.get('metrics', {})
        post_metrics = post_test.get('metrics', {})
        
        if pre_metrics or post_metrics:
            lines.extend([
                "**Performance Metrics**:",
                "",
                "| Metric | Pre | Post | Change |",
                "|--------|-----|------|--------|"
            ])
            
            all_metrics = set(pre_metrics.keys()) | set(post_metrics.keys())
            for metric in sorted(all_metrics):
                pre_val = pre_metrics.get(metric, 'N/A')
                post_val = post_metrics.get(metric, 'N/A')
                
                if isinstance(pre_val, (int, float)) and isinstance(post_val, (int, float)):
                    if metric == 'accessibility_score':
                        change = f"{((post_val - pre_val) / pre_val * 100):+.1f}%" if pre_val != 0 else 'N/A'
                    else:
                        change = f"{((post_val - pre_val) / pre_val * 100):+.1f}%" if pre_val != 0 else 'N/A'
                else:
                    change = 'N/A'
                
                lines.append(f"| {metric} | {format_metric(pre_val)} | {format_metric(post_val)} | {change} |")
            
            lines.extend(["", ""])
    
    return lines

def main():
    """Main function to generate comparison report"""
    workspace_root = Path(__file__).parent
    
    # Load results
    pre_results = load_results(workspace_root / 'Project_A_PreImprove_UI', 'pre')
    post_results = load_results(workspace_root / 'Project_B_PostImprove_UI', 'post')
    
    # Generate report
    report_content = generate_markdown_report(pre_results, post_results)
    
    # Save report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = workspace_root / 'results' / f'compare_report_{timestamp}.md'
    
    with open(report_file, 'w') as f:
        f.write(report_content)
    
    # Also save as compare_report.md (latest)
    latest_report_file = workspace_root / 'compare_report.md'
    with open(latest_report_file, 'w') as f:
        f.write(report_content)
    
    print(f"Comparison report generated: {report_file}")
    print(f"Latest report available at: {latest_report_file}")
    
    # Generate aggregated results
    aggregated_results = {
        'timestamp': datetime.now().isoformat(),
        'pre_improvement': pre_results,
        'post_improvement': post_results,
        'comparison_summary': {
            'pre_available': pre_results is not None,
            'post_available': post_results is not None,
            'comparison_complete': pre_results is not None and post_results is not None
        }
    }
    
    # Save aggregated results
    aggregated_file = workspace_root / 'results' / f'aggregated_metrics_{timestamp}.json'
    with open(aggregated_file, 'w') as f:
        json.dump(aggregated_results, f, indent=2, default=str)
    
    print(f"Aggregated results saved: {aggregated_file}")

if __name__ == '__main__':
    main()
EOF

# Run comparison generation
echo "Generating comparison report..."
python "$WORKSPACE_ROOT/generate_comparison.py"

# Calculate total execution time
EXECUTION_END=$(date +%s)
TOTAL_TIME=$((EXECUTION_END - EXECUTION_START))
HOURS=$((TOTAL_TIME / 3600))
MINUTES=$(((TOTAL_TIME % 3600) / 60))
SECONDS=$((TOTAL_TIME % 60))

echo ""
echo "======================================================="
echo "EXECUTION COMPLETE"
echo "======================================================="
echo "Total execution time: ${HOURS}h ${MINUTES}m ${SECONDS}s"
echo "Execution started: $(date -d @$EXECUTION_START)"
echo "Execution completed: $(date)"
echo ""
echo "Generated artifacts:"
echo "  📊 Comparison report: compare_report.md"
echo "  📁 Detailed results: results/"
echo "  📋 Execution log: $EXECUTION_LOG"
echo ""
echo "To view the comparison report:"
echo "  cat compare_report.md"
echo ""
echo "To open results in browser (if markdown viewer available):"
echo "  # On Windows: start compare_report.md"
echo "  # On Mac: open compare_report.md"  
echo "  # On Linux: xdg-open compare_report.md"
echo ""

# Final status check
if [ -f "$WORKSPACE_ROOT/compare_report.md" ]; then
    echo "✅ UI/UX Improvement evaluation completed successfully!"
    exit 0
else
    echo "❌ Comparison report generation failed. Check the logs for details."
    exit 1
fi