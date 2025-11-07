# Project A - Pre-Improvement UI

## Overview

This project demonstrates the **BEFORE** state of the task management platform's "Create Task" modal. It exhibits common UI/UX anti-patterns that lead to poor user experience and slow perceived performance.

## Problems Demonstrated

### 1. Eager Loading
- All data (tags, members, attachments) loads simultaneously when modal opens
- User must wait for ALL requests to complete before interacting
- Network waterfall causes significant delays

### 2. Poor Field Ordering
- Less important fields (tags, attachments) are placed at the TOP
- Critical fields (title, due date) are at the BOTTOM
- Users must scroll to reach the most important inputs

### 3. Slow Perceived Performance
- Modal appears to "hang" while loading
- No progressive enhancement
- All-or-nothing loading strategy

### 4. Cluttered UI
- Everything shown at once
- Overwhelming for new users
- Difficult to focus on task at hand

## Architecture

### File Structure
```
src/
  index.html     - Single-page modal with eager loading
  styles.css     - Heavy, cluttered styles
  modal.js       - Eager loading implementation
server/
  server.py      - Static file server (port 8001)
data/
  sample_data.json - Test data
tests/
  test_pre_ui.py - Automated test suite
```

### Loading Sequence (SLOW)

```
1. User clicks "Create Task" button
2. Modal container appears (empty)
3. Parallel data fetching begins:
   - Fetch tags (100-500ms)
   - Fetch members (100-500ms)
   - Fetch attachment config (150-650ms)
4. Wait for ALL fetches to complete
5. Render all fields at once
6. Title field is below the fold (requires scroll)
7. User can finally interact (600-1500ms later)
```

## Running the Project

### Setup
```powershell
# Install dependencies
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
```

### Start Server
```powershell
python server\server.py 8001
```

Visit: http://localhost:8001

### Run Tests
```powershell
.\run_tests.ps1
```

## Test Results

Tests measure:
- **Modal load time**: Time until all data loaded and modal interactive
- **Title visibility**: Whether title field visible without scrolling (usually FALSE)
- **Task creation time**: Total time to complete task creation
- **Error handling**: Validation and error messages

Expected results:
- Modal load: 600-1500ms (SLOW)
- Title visible without scroll: FALSE
- High abandonment on slow networks

## Key Metrics

| Metric | Typical Value | Status |
|--------|--------------|--------|
| Modal Load Time | 800-1200ms | 🔴 Poor |
| Time to Title Visible | 800-1200ms | 🔴 Poor |
| Title Visible w/o Scroll | false | 🔴 Poor |
| Task Create Time | 2000-4000ms | 🔴 Poor |

## Observed Issues

1. **Slow Modal Open**: Users wait 1+ second to see the form
2. **Scroll Required**: Title field not visible initially
3. **Poor Focus Management**: Focus goes to first field (tags), not title
4. **No Loading Feedback**: Spinners shown but no progressive loading
5. **All-or-Nothing**: If one request fails, entire modal is blocked

## Next Steps

See **Project B** for the improved implementation that addresses all these issues.

---

**Note:** This project intentionally demonstrates poor UX for comparison purposes.
