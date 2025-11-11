#!/usr/bin/env bash
set -e
echo "Running Project A tests..."
pushd Project_A_PreImprove_UI
if [ -f run_tests.ps1 ]; then
  pwsh -File run_tests.ps1 -latency 0
else
  ./run_tests.sh
fi
popd

echo "Running Project B tests..."
pushd Project_B_PostImprove_UI
if [ -f run_tests.ps1 ]; then
  pwsh -File run_tests.ps1 -latency 0
else
  ./run_tests.sh
fi
popd

echo "Aggregating results..."
mkdir -p results
cp Project_A_PreImprove_UI/results/results_pre.json results/results_pre.json || true
cp Project_B_PostImprove_UI/results/results_post.json results/results_post.json || true

python - <<'PY'
import json, sys
try:
  pre = json.load(open('results/results_pre.json'))
except: pre = []
try:
  post = json.load(open('results/results_post.json'))
except: post = []
agg = {'pre':pre,'post':post}
json.dump(agg, open('results/aggregated_metrics.json','w'), indent=2)
print('Wrote results/aggregated_metrics.json')
PY

echo "Generating compare_report.md"
python - <<'PY'
import json
agg = json.load(open('results/aggregated_metrics.json'))
with open('compare_report.md','w') as f:
  f.write('# Compare Report\n\n')
  f.write('This is an auto-generated compare report. See results folder.\n')
print('compare_report.md created')
PY

echo "Done"
