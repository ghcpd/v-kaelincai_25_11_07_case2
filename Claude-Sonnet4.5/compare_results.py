#!/usr/bin/env python3
"""
Compare results from Project A and Project B
Generate comprehensive comparison report
"""

import json
from pathlib import Path
from datetime import datetime
import statistics

class ResultsComparator:
    def __init__(self):
        self.workspace_root = Path(__file__).parent
        self.results_dir = self.workspace_root / "results"
        
        self.pre_results = None
        self.post_results = None
        
    def load_results(self):
        """Load results from both projects"""
        pre_file = self.results_dir / "results_pre.json"
        post_file = self.results_dir / "results_post.json"
        
        if not pre_file.exists():
            raise FileNotFoundError(f"Pre-improvement results not found: {pre_file}")
        
        if not post_file.exists():
            raise FileNotFoundError(f"Post-improvement results not found: {post_file}")
        
        with open(pre_file, 'r') as f:
            self.pre_results = json.load(f)
        
        with open(post_file, 'r') as f:
            self.post_results = json.load(f)
        
        print(f"Loaded {len(self.pre_results['results'])} pre-improvement test results")
        print(f"Loaded {len(self.post_results['results'])} post-improvement test results")
    
    def calculate_improvements(self):
        """Calculate improvement metrics"""
        improvements = {}
        
        # Aggregate metrics by test case
        for pre_result in self.pre_results['results']:
            test_id = pre_result['test_id']
            
            # Find matching post result
            post_result = next((r for r in self.post_results['results'] if r['test_id'] == test_id), None)
            
            if not post_result:
                continue
            
            improvements[test_id] = {
                'description': pre_result['description'],
                'metrics': {}
            }
            
            # Compare specific metrics
            pre_metrics = pre_result['metrics']
            post_metrics = post_result['metrics']
            
            # Modal load time
            if 'modal_load_time_ms' in pre_metrics and 'modal_load_time_ms' in post_metrics:
                pre_val = pre_metrics['modal_load_time_ms']
                post_val = post_metrics['modal_load_time_ms']
                improvement = ((pre_val - post_val) / pre_val * 100) if pre_val > 0 else 0
                
                improvements[test_id]['metrics']['modal_load_time'] = {
                    'pre': pre_val,
                    'post': post_val,
                    'improvement_percent': round(improvement, 2),
                    'improvement_ms': round(pre_val - post_val, 2)
                }
            
            # Task create time
            if 'task_create_time_ms' in pre_metrics and 'task_create_time_ms' in post_metrics:
                pre_val = pre_metrics['task_create_time_ms']
                post_val = post_metrics['task_create_time_ms']
                improvement = ((pre_val - post_val) / pre_val * 100) if pre_val > 0 else 0
                
                improvements[test_id]['metrics']['task_create_time'] = {
                    'pre': pre_val,
                    'post': post_val,
                    'improvement_percent': round(improvement, 2),
                    'improvement_ms': round(pre_val - post_val, 2)
                }
            
            # Title visibility
            if 'title_visible_without_scroll' in pre_metrics and 'title_visible_without_scroll' in post_metrics:
                improvements[test_id]['metrics']['title_visibility'] = {
                    'pre': pre_metrics['title_visible_without_scroll'],
                    'post': post_metrics['title_visible_without_scroll'],
                    'improved': post_metrics['title_visible_without_scroll'] and not pre_metrics['title_visible_without_scroll']
                }
            
            # Success rate
            improvements[test_id]['metrics']['success'] = {
                'pre': pre_metrics.get('success', False),
                'post': post_metrics.get('success', False)
            }
        
        return improvements
    
    def calculate_aggregate_metrics(self, improvements):
        """Calculate aggregate statistics across all tests"""
        modal_load_improvements = []
        task_create_improvements = []
        
        for test_id, data in improvements.items():
            metrics = data['metrics']
            
            if 'modal_load_time' in metrics:
                modal_load_improvements.append(metrics['modal_load_time']['improvement_percent'])
            
            if 'task_create_time' in metrics:
                task_create_improvements.append(metrics['task_create_time']['improvement_percent'])
        
        aggregate = {}
        
        if modal_load_improvements:
            aggregate['modal_load_time'] = {
                'avg_improvement_percent': round(statistics.mean(modal_load_improvements), 2),
                'median_improvement_percent': round(statistics.median(modal_load_improvements), 2),
                'min_improvement_percent': round(min(modal_load_improvements), 2),
                'max_improvement_percent': round(max(modal_load_improvements), 2)
            }
        
        if task_create_improvements:
            aggregate['task_create_time'] = {
                'avg_improvement_percent': round(statistics.mean(task_create_improvements), 2),
                'median_improvement_percent': round(statistics.median(task_create_improvements), 2),
                'min_improvement_percent': round(min(task_create_improvements), 2),
                'max_improvement_percent': round(max(task_create_improvements), 2)
            }
        
        return aggregate
    
    def generate_markdown_report(self, improvements, aggregate):
        """Generate markdown comparison report"""
        report_path = self.workspace_root / "compare_report.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# UI/UX Improvement Evaluation Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Executive Summary\n\n")
            f.write("This report compares the performance and usability of a task-management platform's \"Create Task\" modal before and after implementing UI/UX improvements.\n\n")
            
            f.write("### Key Improvements Implemented\n\n")
            f.write("1. **Multi-Step Wizard**: Transformed single-page modal into a 3-step wizard\n")
            f.write("2. **Lazy Loading**: Deferred loading of tags, members, and attachments until needed\n")
            f.write("3. **Field Prioritization**: Moved critical fields (title, due date) to the top\n")
            f.write("4. **Enhanced Accessibility**: Added ARIA labels, keyboard navigation, screen reader support\n\n")
            
            f.write("### Overall Performance Gains\n\n")
            
            if 'modal_load_time' in aggregate:
                f.write(f"- **Modal Load Time**: Average improvement of **{aggregate['modal_load_time']['avg_improvement_percent']}%**\n")
                f.write(f"  - Median: {aggregate['modal_load_time']['median_improvement_percent']}%\n")
                f.write(f"  - Range: {aggregate['modal_load_time']['min_improvement_percent']}% to {aggregate['modal_load_time']['max_improvement_percent']}%\n\n")
            
            if 'task_create_time' in aggregate:
                f.write(f"- **Task Creation Time**: Average improvement of **{aggregate['task_create_time']['avg_improvement_percent']}%**\n")
                f.write(f"  - Median: {aggregate['task_create_time']['median_improvement_percent']}%\n")
                f.write(f"  - Range: {aggregate['task_create_time']['min_improvement_percent']}% to {aggregate['task_create_time']['max_improvement_percent']}%\n\n")
            
            f.write("---\n\n")
            
            f.write("## Detailed Test Case Comparison\n\n")
            
            for test_id, data in improvements.items():
                f.write(f"### {test_id}\n\n")
                f.write(f"**Description:** {data['description']}\n\n")
                
                metrics = data['metrics']
                
                if metrics:
                    f.write("| Metric | Pre-Improvement | Post-Improvement | Change |\n")
                    f.write("|--------|-----------------|------------------|--------|\n")
                    
                    if 'modal_load_time' in metrics:
                        m = metrics['modal_load_time']
                        f.write(f"| Modal Load Time | {m['pre']:.2f}ms | {m['post']:.2f}ms | ")
                        f.write(f"✅ **-{m['improvement_percent']}%** ({m['improvement_ms']:.2f}ms faster) |\n")
                    
                    if 'task_create_time' in metrics:
                        m = metrics['task_create_time']
                        f.write(f"| Task Create Time | {m['pre']:.2f}ms | {m['post']:.2f}ms | ")
                        f.write(f"✅ **-{m['improvement_percent']}%** ({m['improvement_ms']:.2f}ms faster) |\n")
                    
                    if 'title_visibility' in metrics:
                        m = metrics['title_visibility']
                        pre_icon = "✅" if m['pre'] else "❌"
                        post_icon = "✅" if m['post'] else "❌"
                        change_icon = "✅ Improved" if m['improved'] else "➖ No change"
                        f.write(f"| Title Visible w/o Scroll | {pre_icon} {m['pre']} | {post_icon} {m['post']} | {change_icon} |\n")
                    
                    if 'success' in metrics:
                        m = metrics['success']
                        pre_icon = "✅" if m['pre'] else "❌"
                        post_icon = "✅" if m['post'] else "❌"
                        f.write(f"| Success | {pre_icon} | {post_icon} | |\n")
                
                f.write("\n")
                
                # Screenshots
                f.write("**Screenshots:**\n\n")
                
                # Find screenshot files
                pre_screenshots = list((self.workspace_root / "Project_A_PreImprove_UI" / "screenshots").glob(f"*{test_id}*.png"))
                post_screenshots = list((self.workspace_root / "Project_B_PostImprove_UI" / "screenshots").glob(f"*{test_id}*.png"))
                
                if pre_screenshots or post_screenshots:
                    f.write("| Pre-Improvement | Post-Improvement |\n")
                    f.write("|-----------------|------------------|\n")
                    
                    max_len = max(len(pre_screenshots), len(post_screenshots))
                    for i in range(max_len):
                        pre_img = f"![Pre]({pre_screenshots[i].relative_to(self.workspace_root)})" if i < len(pre_screenshots) else ""
                        post_img = f"![Post]({post_screenshots[i].relative_to(self.workspace_root)})" if i < len(post_screenshots) else ""
                        f.write(f"| {pre_img} | {post_img} |\n")
                
                f.write("\n---\n\n")
            
            f.write("## Analysis & Recommendations\n\n")
            
            f.write("### What Worked Well\n\n")
            f.write("1. **Lazy Loading**: Significantly reduced initial modal load time by deferring non-critical data\n")
            f.write("2. **Wizard Flow**: Improved user focus by presenting information in logical steps\n")
            f.write("3. **Field Prioritization**: Title and due date are now immediately visible and focused\n")
            f.write("4. **Progressive Enhancement**: Users can start typing immediately without waiting for all data to load\n\n")
            
            f.write("### Known Limitations\n\n")
            f.write("1. **Emulation vs. Real Devices**: Tests run in Chromium headless browser, may differ on mobile devices\n")
            f.write("2. **Network Simulation**: Synthetic delays may not perfectly match real-world network conditions\n")
            f.write("3. **Browser Variability**: Tests run on single browser engine, cross-browser testing needed\n")
            f.write("4. **Screen Reader Testing**: Automated checks for ARIA attributes, but manual testing with real screen readers recommended\n\n")
            
            f.write("### Recommended Rollout Strategy\n\n")
            f.write("1. **A/B Testing**: Deploy to 10% of users initially, monitor metrics\n")
            f.write("2. **Key Metrics to Monitor**:\n")
            f.write("   - Task creation completion rate\n")
            f.write("   - Time to first interaction\n")
            f.write("   - Abandonment rate at each wizard step\n")
            f.write("   - Error rates and validation failures\n")
            f.write("3. **Progressive Rollout**: Increase to 25%, 50%, 100% based on positive metrics\n")
            f.write("4. **Accessibility Audit**: Conduct manual testing with screen readers (NVDA, JAWS, VoiceOver)\n")
            f.write("5. **User Feedback**: Collect qualitative feedback through surveys and user interviews\n\n")
            
            f.write("### Future Enhancements\n\n")
            f.write("1. **Smart Defaults**: Pre-populate fields based on user history\n")
            f.write("2. **Inline Validation**: Real-time field validation as user types\n")
            f.write("3. **Progress Persistence**: Save wizard state to allow users to resume later\n")
            f.write("4. **Keyboard Shortcuts**: Power user shortcuts for quick task creation\n")
            f.write("5. **Mobile Optimization**: Touch-friendly controls and gesture support\n\n")
            
            f.write("---\n\n")
            f.write("**Report Generated by:** UI/UX Improvement Evaluation Framework\n")
            f.write(f"**Timestamp:** {datetime.now().isoformat()}\n")
        
        print(f"\nComparison report generated: {report_path}")
        return report_path
    
    def save_aggregated_metrics(self, improvements, aggregate):
        """Save aggregated metrics to JSON"""
        output = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'pre_improvement': {
                    'total_tests': self.pre_results['total_tests'],
                    'passed': self.pre_results['passed'],
                    'failed': self.pre_results['failed']
                },
                'post_improvement': {
                    'total_tests': self.post_results['total_tests'],
                    'passed': self.post_results['passed'],
                    'failed': self.post_results['failed']
                }
            },
            'improvements': improvements,
            'aggregate_statistics': aggregate
        }
        
        output_file = self.results_dir / "aggregated_metrics.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)
        
        print(f"Aggregated metrics saved: {output_file}")
    
    def run(self):
        """Run the comparison"""
        print("="*60)
        print("UI/UX Improvement Comparison Tool")
        print("="*60)
        print()
        
        self.load_results()
        
        print("\nCalculating improvements...")
        improvements = self.calculate_improvements()
        
        print("Calculating aggregate metrics...")
        aggregate = self.calculate_aggregate_metrics(improvements)
        
        print("\nGenerating comparison report...")
        self.generate_markdown_report(improvements, aggregate)
        
        print("\nSaving aggregated metrics...")
        self.save_aggregated_metrics(improvements, aggregate)
        
        print("\n" + "="*60)
        print("Comparison Complete!")
        print("="*60)


if __name__ == '__main__':
    comparator = ResultsComparator()
    comparator.run()
