# UI/UX Improvement Experiment

This repo contains two demo projects and a test harness to evaluate a UI improvement: converting a Create Task modal into a multi-step wizard, lazy loading heavy content, and reordering fields to prioritize title and due date.

Run everything end-to-end:
1. From the repo root, run `run_all.sh`. This will create virtual environments, install dependencies, run both servers and Playwright tests across the canonical test cases defined in `shared_artifacts/test_data.json`.
2. Results and artifacts will be saved in `results` and each project's `screenshots` and `logs` folders.

Acceptance criteria and thresholds are defined in `PROJECT_REQUIREMENTS.md`.

Limitations & notes:
- This demo uses browser automation to emulate real user behavior — results vary across browsers and machines.
- Network latency is simulated by query params and server-side delays; it is not an accurate proxy for real mobile networks.
- Playwright must be installed and will download browser binaries during setup.
- For production evaluation, integrate A/B testing with telemetry and progressive rollout.
