#!/usr/bin/env python3
import json
import argparse
from statistics import mean, median


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--pre', required=True)
    p.add_argument('--post', required=True)
    p.add_argument('--out', required=True)
    return p.parse_args()


def compute_metrics(results):
    metrics = {}
    for case_id, runs in results.items():
        modal_open = [r.get('modal_open_ms', -1) for r in runs]
        title_visible = [r.get('time_to_title_visible_ms', -1) for r in runs]
        task_create = [r.get('task_create_ms', -1) for r in runs]
        success = [1 if r.get('task_created') else 0 for r in runs]
        metrics[case_id] = {
            'avg_modal_open_ms': mean([v for v in modal_open if v>0]) if any(v>0 for v in modal_open) else -1,
            'median_task_create_ms': median([v for v in task_create if v>0]) if any(v>0 for v in task_create) else -1,
            'avg_title_visible_ms': mean([v for v in title_visible if v>0]) if any(v>0 for v in title_visible) else -1,
            'success_rate': sum(success) / len(success) if len(success) > 0 else 0,
            'raw_runs': runs
        }
    return metrics


def main():
    args = parse_args()
    with open(args.pre, 'r') as f:
        pre = json.load(f)
    with open(args.post, 'r') as f:
        post = json.load(f)

    pre_metrics = compute_metrics(pre)
    post_metrics = compute_metrics(post)

    # compute improvements
    improvements = {}
    for k in pre_metrics:
        pre_m = pre_metrics[k]
        post_m = post_metrics.get(k, {})
        def pct_delta(pre_v, post_v):
            if pre_v is None or post_v is None or pre_v<=0:
                return None
            return (pre_v - post_v) / pre_v
        improvements[k] = {
            'modal_open_ms_reduction': pct_delta(pre_m.get('avg_modal_open_ms', -1), post_m.get('avg_modal_open_ms', -1)),
            'task_create_ms_reduction': pct_delta(pre_m.get('median_task_create_ms', -1), post_m.get('median_task_create_ms', -1)),
            'title_visible_ms_reduction': pct_delta(pre_m.get('avg_title_visible_ms', -1), post_m.get('avg_title_visible_ms', -1)),
            'success_rate_delta': (post_m.get('success_rate',0) - pre_m.get('success_rate',0)),
            'pre': pre_m,
            'post': post_m
        }

    aggregated = {
        'pre_metrics': pre_metrics,
        'post_metrics': post_metrics,
        'improvements': improvements
    }

    with open(args.out, 'w') as f:
        json.dump(aggregated, f, indent=2)

if __name__ == '__main__':
    main()
