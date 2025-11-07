#!/bin/bash
set -e
ROOT_DIR=$(pwd)
# Setup environments
echo "Setting up Project A..."
cd Project_A_PreImprove_UI
./setup.sh || true

echo "Running Project A tests..."
./run_tests.sh
cd $ROOT_DIR

# Run Project B
echo "Setting up Project B..."
cd Project_B_PostImprove_UI
./setup.sh || true

echo "Running Project B tests..."
./run_tests.sh
cd $ROOT_DIR

# Aggregate results
mkdir -p results
cp Project_A_PreImprove_UI/results/results_pre.json results/results_pre.json
cp Project_B_PostImprove_UI/results/results_post.json results/results_post.json

python tools/generate_compare_report.py --pre results/results_pre.json --post results/results_post.json --out results/aggregated_metrics.json
python tools/format_compare_report.py --pre results/results_pre.json --post results/results_post.json --out compare_report.md
python tools/collect_artifacts.py

echo "Done. Reports available: compare_report.md and results/aggregated_metrics.json"
