# Project B - Post-Improvement UI

This demo implements the improved UX:

- Modal transformed into a step-by-step wizard
- Lazy loading for heavy modules (tags and attachments)
- Title and due date prioritized and visible on first step
- Improved accessibility and keyboard focus management

How to run:
- Windows PowerShell:
  - python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt; python -m playwright install
  - Start server: python server/server.py --port 8001
  - Run tests: python -m pytest tests/test_post_ui.py -- --port 8001 --repeat 3

- Or run run_tests.sh in Git Bash or WSL. To customize: ./run_tests.sh <port> <repeat_count>

Where to find artifacts:
- results/results_post.json
- screenshots/
- logs/log_post.txt

This project's tests specifically check lazy load behavior, accessibility, and optimized field visibility.
