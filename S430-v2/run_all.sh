@echo off
setlocal
call Project_A_PreImprove_UI\setup.sh
call Project_B_PostImprove_UI\setup.sh
call Project_A_PreImprove_UI\run_tests.sh 1000
call Project_B_PostImprove_UI\run_tests.sh 1000
mkdir results 2>nul
xcopy /Y /S Project_A_PreImprove_UI\results results\Project_A_PreResults 1>nul
xcopy /Y /S Project_B_PostImprove_UI\results results\Project_B_PostResults 1>nul
xcopy /Y /S Project_A_PreImprove_UI\screenshots results\Project_A_Screenshots 1>nul
xcopy /Y /S Project_B_PostImprove_UI\screenshots results\Project_B_Screenshots 1>nul
xcopy /Y /S Project_A_PreImprove_UI\logs results\Project_A_Logs 1>nul
xcopy /Y /S Project_B_PostImprove_UI\logs results\Project_B_Logs 1>nul
python - <<'PY'
import json
from pathlib import Path
from glob import glob
pre_files = sorted(glob('Project_A_PreImprove_UI/results/results_pre_*.json'))
post_files = sorted(glob('Project_B_PostImprove_UI/results/results_post_*.json'))
cases = []
pre_agg = {}
post_agg = {}
for pf in pre_files:
    name = Path(pf).stem.replace('results_pre_','')
    pre = json.loads(Path(pf).read_text())
    pre_agg[name] = pre
    post = json.loads(Path(f'Project_B_PostImprove_UI/results/results_post_{name}.json').read_text())
    post_agg[name] = post
    modal_improve = None
    task_improve = None
    if pre.get('modal_load_ms') and post.get('modal_load_ms'):
        modal_improve = (pre['modal_load_ms']-post['modal_load_ms'])/pre['modal_load_ms']*100 if pre['modal_load_ms']>0 else 0
    if pre.get('task_create_ms') and post.get('task_create_ms'):
        task_improve = (pre['task_create_ms']-post['task_create_ms'])/pre['task_create_ms']*100 if pre['task_create_ms']>0 else 0
    cases.append({'id':name, 'pre':pre, 'post':post, 'modal_improve_pct':modal_improve, 'task_improve_pct':task_improve})
agg = {'cases': cases}
Path('results/aggregated_metrics.json').write_text(json.dumps(agg, indent=2))
Path('results/results_pre.json').write_text(json.dumps(pre_agg, indent=2))
Path('results/results_post.json').write_text(json.dumps(post_agg, indent=2))
# thresholds
modal_thresh = 30.0
task_thresh = 20.0
md = ['# Compare Report\n']
md.append('## Executive summary\n- Numeric thresholds: modal_load_ms reduced by >=30%, task_create_ms reduced by >=20%\n\n')
from statistics import mean, median
for c in cases:
    # compute aggregates across possible repeats
    pre_list = [json.loads(Path(pf).read_text()) for pf in pre_files if Path(pf).stem.replace('results_pre_','')==c['id']]
    post_list = [json.loads(f.read_text()) for f in [Path(f'Project_B_PostImprove_UI/results/results_post_{c["id"]}.json')]]
    # fallback to using single measurements
    pre_modal_vals = [x.get('modal_load_ms',0) for x in pre_list if x.get('modal_load_ms') is not None]
    post_modal_vals = [x.get('modal_load_ms',0) for x in [json.loads(Path(f'Project_B_PostImprove_UI/results/results_post_{c["id"]}.json').read_text())] if x.get('modal_load_ms') is not None]
    pre_task_vals = [x.get('task_create_ms',0) for x in pre_list if x.get('task_create_ms')]
    post_task_vals = [x.get('task_create_ms',0) for x in [json.loads(Path(f'Project_B_PostImprove_UI/results/results_post_{c["id"]}.json').read_text())] if x.get('task_create_ms')]
    avg_pre_modal = mean(pre_modal_vals) if pre_modal_vals else None
    avg_post_modal = mean(post_modal_vals) if post_modal_vals else None
    avg_pre_task = mean(pre_task_vals) if pre_task_vals else None
    med_pre_task = median(pre_task_vals) if pre_task_vals else None
    med_post_task = median(post_task_vals) if post_task_vals else None
    mp = None
    tp = None
    if avg_pre_modal and avg_post_modal:
        mp = (avg_pre_modal - avg_post_modal)/avg_pre_modal*100
    if med_pre_task and med_post_task:
        tp = (med_pre_task - med_post_task)/med_pre_task*100
    title_pre = c['pre'].get('title_visible')
    title_post = c['post'].get('title_visible')
    modal_pass = mp >= modal_thresh
    task_pass = tp >= task_thresh
    title_pass = bool(title_post)
    screenshot_pre = f"Project_A_PreImprove_UI/screenshots/screenshot_pre_{c['id']}.png"
    screenshot_post = f"Project_B_PostImprove_UI/screenshots/screenshot_post_{c['id']}.png"
    # malformed input: expect a POST failure
    malformed_ok = True
    if c['id'] == 'malformed':
        malformed_ok = not c['post'].get('task_success', True)
    # accessibility quick check: expect title to have role/name
    a11y_ok = True
    if c['id'] == 'accessibility':
        a1 = c['post'].get('a11y')
        a11y_ok = (a1 is not None)
    md.append(f"## Case {c['id']}\n")
    md.append(f"- Pre modal load (ms): {c['pre'].get('modal_load_ms')}\n- Post modal load (ms): {c['post'].get('modal_load_ms')}\n- Modal improve pct: {mp}\n- Modal PASS: {modal_pass}\n- Pre task time (ms): {c['pre'].get('task_create_ms')}\n- Post task time (ms): {c['post'].get('task_create_ms')}\n- Task improve pct: {tp}\n- Task PASS: {task_pass}\n- Title visible pre: {title_pre}\n- Title visible post: {title_post}\n- Title PASS: {title_pass}\n- Malformed PASS: {malformed_ok}\n- Accessibility PASS: {a11y_ok}\n- Pre screenshot: ![]({screenshot_pre})\n- Post screenshot: ![]({screenshot_post})\n\n")
Path('compare_report.md').write_text('\n'.join(md))
print('Done')
PY
