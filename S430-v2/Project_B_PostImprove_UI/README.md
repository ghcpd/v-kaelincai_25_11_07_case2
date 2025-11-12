Project B — Post-Improvement

This demo converts the modal into a 3-step wizard and lazily loads heavy modules (tags, attachments) only when the user reaches that step. Title and Due Date are moved to the first step.

Run tests:
- Windows: `run_tests.sh [latency_ms]`
- Runs the Flask server then Playwright test that captures modal load time, first-field visibility, and task creation time.

Artifacts: `results/results_post.json`, `screenshots`, `logs/log_post.txt`.
