#!/usr/bin/env bash
set -e
# Run pre
cd Project_A_PreImprove_UI
pwsh -File run_tests.ps1
cd ..
# Run post
cd Project_B_PostImprove_UI
pwsh -File run_tests.ps1
cd ..
# aggregate
python - << 'PY'
import json
with open('Project_A_PreImprove_UI/results/results_pre.json') as f: pre_d=json.load(f)
with open('Project_B_PostImprove_UI/results/results_post.json') as f: post_d=json.load(f)
aggr={'pre':pre_d,'post':post_d}
with open('results/aggregated_metrics.json','w') as f:
    json.dump(aggr,f,indent=2)

# compute simple deltas
report = []
for key in ['time_to_title_visible_ms','task_create_ms']:
    a=pre_d.get(key,0)
    b=post_d.get(key,0)
    if a>0:
        delta = (a-b)/a*100
    else:
        delta = 0
    report.append((key,a,b,delta))

with open('compare_report.md','w') as f:
    f.write('# Comparison Report\n\n')
    f.write('## Metrics\n')
    for k,a,b,delta in report:
        f.write(f'* {k}: pre={a}ms, post={b}ms, delta={delta:.1f}%\n')
    f.write('\n## Executive Summary\n')
    f.write('See results/aggregated_metrics.json for full details.\n')
print('Compare report written')
PY
