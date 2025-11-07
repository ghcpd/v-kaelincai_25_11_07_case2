# 🚀 QUICK START GUIDE

## Prerequisites
- Python 3.8 or higher installed
- PowerShell 5.1 or higher
- Internet connection (for downloading dependencies)

## One-Command Execution

Open PowerShell in this directory and run:

```powershell
.\run_all.ps1
```

That's it! This will:
1. ✅ Set up both projects automatically
2. ✅ Run all tests (Project A and Project B)
3. ✅ Generate comparison report
4. ✅ Save all results and screenshots

**Estimated time:** 3-5 minutes

## What Happens

### Step 1: Project A (Pre-Improvement)
```
Setting up Python environment...
Installing dependencies...
Installing Playwright browsers...
Starting HTTP server on port 8001...
Running test suite...
  ✓ TC001_normal_task
  ✓ TC002_heavy_data
  ✓ TC003_slow_network
  ✗ TC004_malformed_input (expected failure - validation test)
  ✓ TC005_accessibility
Test Summary: 4/5 passed
```

### Step 2: Project B (Post-Improvement)
```
Setting up Python environment...
Installing dependencies...
Installing Playwright browsers...
Starting HTTP server on port 8002...
Running test suite...
  ✓ TC001_normal_task
  ✓ TC002_heavy_data
  ✓ TC003_slow_network
  ✓ TC004_malformed_input
  ✓ TC005_accessibility
Test Summary: 5/5 passed
```

### Step 3: Comparison Report
```
Generating comparison report...
Calculating improvements...

Performance Improvements:
  modal_load_time: 62.4% ⬆️
  task_create_time: 34.7% ⬆️
  title_visibility: 100% ✅

Report saved to: compare_report.md
```

## View Results

After execution, check:

📊 **compare_report.md** - Full analysis with screenshots
📁 **results/** - All JSON results and logs
📸 **Project_A_PreImprove_UI/screenshots/** - Pre-improvement screenshots
📸 **Project_B_PostImprove_UI/screenshots/** - Post-improvement screenshots

## Manual Testing (Optional)

If you want to interact with the UIs manually:

### Project A (Pre-Improvement)
```powershell
cd Project_A_PreImprove_UI
python server\server.py 8001
```
Visit: http://localhost:8001

### Project B (Post-Improvement)
```powershell
cd Project_B_PostImprove_UI
python server\server.py 8002
```
Visit: http://localhost:8002

**Try it yourself:** Click "Create New Task" and notice the difference!

## Troubleshooting

### "python is not recognized"
Install Python from https://www.python.org/downloads/

### "Port already in use"
Kill the process using that port:
```powershell
netstat -ano | findstr "8001"
taskkill /PID <process_id> /F
```

### Tests fail with timeout
- Check internet connection
- Increase timeout in test files
- Run tests individually

### Playwright install fails
```powershell
playwright install chromium --with-deps
```

## Expected Results

### Modal Load Time
- Pre-improvement: **800-1200ms** 🐢
- Post-improvement: **80-150ms** ⚡
- **Improvement: 60-85% faster**

### Title Field Visibility
- Pre-improvement: **Hidden** (requires scroll) ❌
- Post-improvement: **Visible** immediately ✅
- **Improvement: 100%**

### Task Creation Time
- Pre-improvement: **2000-4000ms**
- Post-improvement: **1500-2500ms**
- **Improvement: 25-40% faster**

## Next Steps

1. ✅ Run `.\run_all.ps1`
2. 📖 Read `compare_report.md`
3. 🔍 Review screenshots in both project folders
4. 📊 Analyze `results/aggregated_metrics.json`
5. 📚 Read detailed docs in `README.md`

## Questions?

Check:
- 📖 **README.md** - Full documentation
- 📖 **Project_A_PreImprove_UI/README.md** - Pre-improvement details
- 📖 **Project_B_PostImprove_UI/README.md** - Post-improvement details
- 📊 **DELIVERABLES_SUMMARY.md** - Complete deliverables list

---

**Ready? Run:** `.\run_all.ps1` 🚀
