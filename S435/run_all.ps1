# PowerShell script to run both projects end-to-end
param(
    [int]$repeat = 3
)

Write-Host "Running Project A (pre-improvement)"
Push-Location Project_A_PreImprove_UI
# setup
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install
# run
.\run_tests.ps1 -Port 8000 -Repeat $repeat
Pop-Location

Write-Host "Running Project B (post-improvement)"
Push-Location Project_B_PostImprove_UI
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install
.\run_tests.ps1 -Port 8001 -Repeat $repeat
Pop-Location

# aggregate
python tools/generate_compare_report.py --pre results/results_pre.json --post results/results_post.json --out results/aggregated_metrics.json
python tools/format_compare_report.py --pre results/results_pre.json --post results/results_post.json --out compare_report.md
python tools/collect_artifacts.py
Write-Host "Done. Reports available: compare_report.md and results/aggregated_metrics.json"
