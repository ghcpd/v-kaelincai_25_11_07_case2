Test scenario: Transform Create Task modal to wizard + lazy load.

Expected test input JSON structure in `test_data.json`: [
  {"id":"...","description":"...","input":{...},"env":{"networkLatency":50,"tagCount":10}, "expected":{...} }
]

Acceptance criteria:
- Modal load time (modal_load_ms) reduced by >=30%
- Task create time (task_create_ms) reduced by >=20%
- Title visible in first screen (title_visible True) for post-improvement

Outputs: Per-case JSON for pre/post are under `Project_A_PreImprove_UI/results` and `Project_B_PostImprove_UI/results` and aggregated JSON in `results/aggregated_metrics.json`.
