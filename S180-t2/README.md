# UI/UX Improvement Experiments

Run all tests and compare pre/post improvements for the Create Task modal.

Quick start (PowerShell):
* cd Project_A_PreImprove_UI; .\setup.ps1; .\run_tests.ps1
* cd ../Project_B_PostImprove_UI; .\setup.ps1; .\run_tests.ps1
* cd ..; ./run_all.sh  (bash)  OR run the commands in order manually in PowerShell.

Acceptance Criteria:
* modal_load_ms reduced by >=30%
* task_create_ms reduced by >=20%
* first_field_visibility >=95%

See compare_report.md and results/ for artifacts.
