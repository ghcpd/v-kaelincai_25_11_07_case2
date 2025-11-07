#!/usr/bin/env python3
import json
import argparse
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--pre', required=True)
    p.add_argument('--post', required=True)
    p.add_argument('--out', required=True)
    return p.parse_args()


def format_percentage(v):
    if v is None:
        return 'N/A'
    try:
        return f"{v*100:.1f}%"
    except Exception:
        return 'N/A'


def main():
    args = parse_args()
    with open(args.pre, 'r') as f:
        pre = json.load(f)
    with open(args.post, 'r') as f:
        post = json.load(f)

    # Prefer aggregated metrics if present
    agg_file = Path('results') / 'aggregated_metrics.json'
    pre_metrics = pre
    post_metrics = post
    try:
        if agg_file.exists():
            with open(agg_file, 'r') as af:
                agg = json.load(af)
                pre_metrics = agg.get('pre_metrics', {})
                post_metrics = agg.get('post_metrics', {})
                improvements = agg.get('improvements', {})
        else:
            improvements = {}
    except Exception:
        improvements = {}

    md_lines = []
    md_lines.append('# Compare Report')
    md_lines.append('\n')
    md_lines.append('## Executive Summary')
    md_lines.append('\n')
    md_lines.append('- This comparison evaluates the transformation from a single modal (Pre) to a step-by-step wizard with lazy-loaded heavy resources (Post).')
    md_lines.append('- Success thresholds: modal_load_ms reduced by >=30%, task_create_ms reduced by >=20%, title visible without scroll >=95%.')
    md_lines.append('\n')

    md_lines.append('## Results per Test Case')
    md_lines.append('\n')

    cases = set(list(pre.keys()) + list(post.keys()) + list(pre_metrics.keys()))

    for case_id in cases:
        md_lines.append(f'### Case: {case_id}\n')

        # show run-level data
        pre_runs = pre.get(case_id, [])
        post_runs = post.get(case_id, [])
        md_lines.append('- **Pre-Improvement**')
        for r in pre_runs:
            md_lines.append(f"  - modal_open_ms: {r.get('modal_open_ms')}, title_visible_ms: {r.get('time_to_title_visible_ms')}, task_create_ms: {r.get('task_create_ms')}, created: {r.get('task_created')}")
        md_lines.append('\n- **Post-Improvement**')
        for r in post_runs:
            md_lines.append(f"  - modal_open_ms: {r.get('modal_open_ms')}, title_visible_ms: {r.get('time_to_title_visible_ms')}, task_create_ms: {r.get('task_create_ms')}, created: {r.get('task_created')}")

        # aggregated metrics
        pre_m = pre_metrics.get(case_id, {})
        post_m = post_metrics.get(case_id, {})
        imp = improvements.get(case_id, {})

        # add screenshots if they exist
        pre_first = Path('Project_A_PreImprove_UI') / 'screenshots' / f'screenshot_pre_{case_id}_first.png'
        pre_final = Path('Project_A_PreImprove_UI') / 'screenshots' / f'screenshot_pre_{case_id}_final.png'
        post_first = Path('Project_B_PostImprove_UI') / 'screenshots' / f'screenshot_post_{case_id}_first.png'
        post_final = Path('Project_B_PostImprove_UI') / 'screenshots' / f'screenshot_post_{case_id}_final.png'

        if pre_first.exists() or post_first.exists():
            md_lines.append('\n- **Screenshots**')
            if pre_first.exists():
                md_lines.append(f"  - Pre first view: ![pre-first]({pre_first.as_posix()})")
            if pre_final.exists():
                md_lines.append(f"  - Pre final: ![pre-final]({pre_final.as_posix()})")
            if post_first.exists():
                md_lines.append(f"  - Post first view: ![post-first]({post_first.as_posix()})")
            if post_final.exists():
                md_lines.append(f"  - Post final: ![post-final]({post_final.as_posix()})")


        md_lines.append('\n- **Aggregated Metrics**')
        md_lines.append(f"  - Pre avg_modal_open_ms: {pre_m.get('avg_modal_open_ms', 'N/A')}")
        md_lines.append(f"  - Post avg_modal_open_ms: {post_m.get('avg_modal_open_ms', 'N/A')}")
        md_lines.append(f"  - Modal load reduction: {format_percentage(imp.get('modal_open_ms_reduction'))}")

        md_lines.append(f"  - Pre median_task_create_ms: {pre_m.get('median_task_create_ms', 'N/A')}")
        md_lines.append(f"  - Post median_task_create_ms: {post_m.get('median_task_create_ms', 'N/A')}")
        md_lines.append(f"  - Task create reduction: {format_percentage(imp.get('task_create_ms_reduction'))}")

        md_lines.append(f"  - Pre avg_title_visible_ms: {pre_m.get('avg_title_visible_ms', 'N/A')}")
        md_lines.append(f"  - Post avg_title_visible_ms: {post_m.get('avg_title_visible_ms', 'N/A')}")
        md_lines.append(f"  - Title visible reduction: {format_percentage(imp.get('title_visible_ms_reduction'))}")

        md_lines.append(f"  - Pre success_rate: {pre_m.get('success_rate', 'N/A')}")
        md_lines.append(f"  - Post success_rate: {post_m.get('success_rate', 'N/A')}")
        md_lines.append(f"  - Success rate delta: {format_percentage(imp.get('success_rate_delta')) if imp.get('success_rate_delta') is not None else 'N/A'}")

        # Pass/Fail by thresholds
        modal_ok = imp.get('modal_open_ms_reduction') is not None and imp.get('modal_open_ms_reduction') >= 0.30
        task_ok = imp.get('task_create_ms_reduction') is not None and imp.get('task_create_ms_reduction') >= 0.20
        title_ok = post_m.get('avg_title_visible_ms') is not None and post_m.get('avg_title_visible_ms')>0 and (post_m.get('avg_title_visible_ms') <= pre_m.get('avg_title_visible_ms') )
        success_ok = post_m.get('success_rate', 0) >= 0.90

        md_lines.append('\n- **Pass/Fail**')
        md_lines.append(f"  - Modal improvement (>=30% faster): {'PASS' if modal_ok else 'FAIL'}")
        md_lines.append(f"  - Task create improvement (>=20% faster): {'PASS' if task_ok else 'FAIL'}")
        md_lines.append(f"  - Title visibility improved: {'PASS' if title_ok else 'FAIL'}")
        md_lines.append(f"  - Success rate >= 90%: {'PASS' if success_ok else 'FAIL'}")

        md_lines.append('\n---\n')

    with open(args.out, 'w') as of:
        of.write('\n'.join(md_lines))

    print('compare_report.md written')

if __name__ == '__main__':
    main()
