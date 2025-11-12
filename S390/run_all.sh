@echo off
setlocal
REM Run Project A pre-improvement tests
cd Project_A_PreImprove_UI
call setup.sh
call run_tests.sh 1
cd ..
REM Run Project B post-improvement tests
cd Project_B_PostImprove_UI
call setup.sh
call run_tests.sh 1
cd ..
REM Generate report
python shared\scripts\generate_report.py
echo Done. Compare report at compare_report.md
pause