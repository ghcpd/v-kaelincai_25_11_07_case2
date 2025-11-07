# Test Case Descriptions

This document describes the test cases in `test_data.json` and the rationale for each. These are used by the automated Playwright tests to evaluate pre/post improvements.

1) normal_case
- Verifies: A typical task creation with title, assignee, and due date.
- Importance: This baseline represents the most common common flow — any UX regression here is critical.
- Checks: Modal opens, title/due date are visible, task can be created.

2) heavy_data_case
- Verifies: Behaviour when many tags and large attachments exist.
- Importance: Ensures lazy loading is effective and application snappy under heavy data.
- Checks: Tags/attachments are loaded lazily, initial modal open quick, no perceived jank.

3) slow_network_case
- Verifies: UX under high latency (e.g., 3G-like).
- Importance: Confirms improvements degrade gracefully and allow the user to type while heavy resources load.
- Checks: Title/due date visible immediately, lazy load shows progress, submission still possible once dependencies arrive.

4) malformed_input_case
- Verifies: Proper validation and error messaging for broken inputs.
- Importance: Prevents data corruption and poor UX.
- Checks: Validation errors show, submission prevented, no JS crashes.

5) accessibility_case
- Verifies: Keyboard navigation, ARIA roles and focus order.
- Importance: Ensures the UI remains accessible to keyboard/screen reader users.
- Checks: Tab order is logical, screen-reader labels exist, focus indicators visible.


Acceptance Criteria Summary
- Modal open time must reduce by at least 30% in post-improvement vs pre-improvement where applicable.
- Task create time must reduce by at least 20%.
- Title/due date must be visible on the first screen in the post-improvement (>=95% of runs).
- No regression in success rate or accessibility checks.
