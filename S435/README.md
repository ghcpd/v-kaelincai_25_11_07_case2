# UI/UX Improvement Evaluation

This repository contains two projects demonstrating a UI/UX improvement: transforming a Create Task modal (pre-improvement) into a multi-step wizard with lazy loading and field prioritization (post-improvement). The test harness uses Playwright to measure timings, verify lazy loading, and ensure accessibility and validation are preserved.

How to run the complete experiment on Windows:

1. Install Python 3.10+ and ensure `python` is on PATH.
2. Create and activate a virtual environment, then install dependencies for both projects.
   - PowerShell commands (from the repo root):
     - python -m venv venv
     - .\venv\Scripts\Activate.ps1
     - pip install -r Project_A_PreImprove_UI/requirements.txt
     - python -m playwright install
     - pip install -r Project_B_PostImprove_UI/requirements.txt
     - python -m playwright install
3. Run the full experiment:
   - In PowerShell: bash ./run_all.sh
   - Or call each project's run_tests.sh directly and pass optional port and repeat, e.g.:
     - ./Project_A_PreImprove_UI/run_tests.sh 8000 3
     - ./Project_B_PostImprove_UI/run_tests.sh 8001 3

Artifacts produced:
- results/results_pre.json
- results/results_post.json
- results/aggregated_metrics.json
- compare_report.md
- Screenshots in each project under `screenshots/`
- Logs under each project's `logs/`

Limitations:
- Simulated network latency via localStorage; real-world latency varies by region/device.
- Playwright headless runs may differ from actual user interactions; consider running in headed mode for visual inspection.
- Tests focus on single-browser Chromium; add cross-browser runs for production evaluation.

Recommendations for rollout:
- Perform an A/B test targeting a subset of users (5-10%) and measure live metrics for perceived latency and task completion success.
- Monitor telemetry for field visibility, time to completion, and error rates; roll back if regressions appear.
- Implement analytics for lazy loading hits and network savings.

