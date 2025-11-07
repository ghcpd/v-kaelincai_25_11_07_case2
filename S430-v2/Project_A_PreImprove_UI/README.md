Project A — Pre-Improvement

This demo shows a modal that eagerly loads tags and attachments when opened. Fields like Title and Due Date are placed far down the form. The goal is to measure a baseline and then compare against a post-improvement pattern.

Run tests:
- Windows: `run_tests.sh [latency_ms]`
- Runs the Flask server then Playwright test that captures modal load time, first-field visibility, and task creation time.

Artifacts: `results/results_pre.json`, `screenshots`, `logs/log_pre.txt`.
