# Project A - Pre-Improvement UI

This demo reproduces the original modal behavior with eager loading and poor field order that lead to sluggish performance:

- Eager loading of tags, members, and attachments during modal open
- Critical fields (title, due date) placed near the bottom of the modal
- Poor accessibility and keyboard navigation

How to run:

- On Windows PowerShell:
  - python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt; python -m playwright install
  - Start server: python server/server.py --port 8000
  - Run tests: python -m pytest tests/test_pre_ui.py -- --port 8000 --repeat 3

- For convenience: run run_tests.sh (in Git Bash / WSL) or run the commands above in PowerShell. To customize: ./run_tests.sh <port> <repeat_count>

Where to find artifacts:
- results/results_pre.json: machine-readable timing and pass/fail data
- screenshots/: screenshots for each test case
- logs/log_pre.txt: run logs
