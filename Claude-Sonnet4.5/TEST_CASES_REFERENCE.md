# Test Cases Reference Guide

## Overview
This document provides detailed information about the 5 comprehensive test cases used to evaluate UI/UX improvements.

---

## Test Case Index

| ID | Name | Category | Environment | Expected Result |
|----|------|----------|-------------|-----------------|
| TC001 | Normal Task | Baseline | Low latency | Pass |
| TC002 | Heavy Data | Stress Test | High load | Pass |
| TC003 | Slow Network | Performance | High latency | Pass |
| TC004 | Malformed Input | Validation | Normal | Fail (expected) |
| TC005 | Accessibility | A11y | Normal | Pass |

---

## TC001: Normal Task Creation

### Description
Typical user workflow - creating a standard task with basic fields.

### Test Scenario
A user creates a routine task with:
- Clear title
- Reasonable due date
- Single assignee
- Few tags
- No attachments

### Input Data
```json
{
  "task_title": "Review Q4 budget proposal",
  "task_description": "Review and approve the Q4 budget for marketing department",
  "assignee": "john.doe@company.com",
  "due_date": "2025-11-15",
  "priority": "high",
  "tags": ["budget", "review"],
  "attachments": []
}
```

### Environment Configuration
```json
{
  "network_latency_ms": 50,
  "tag_count": 10,
  "member_count": 5,
  "attachment_size_kb": 0
}
```

### Expected Metrics
- **Modal Load Time**: ≤500ms (pre), ≤200ms (post)
- **Time to Title Visible**: ≤200ms (pre), ≤100ms (post)
- **Task Create Time**: ≤3000ms (pre), ≤2000ms (post)
- **Title Visible Without Scroll**: false (pre), true (post)

### Pass Criteria
- [x] Modal opens successfully
- [x] All fields accessible
- [x] Task created successfully
- [x] No errors

### What This Tests
- Basic functionality
- Normal performance baseline
- User experience for typical workflow

---

## TC002: Heavy Data Load

### Description
Stress test with many tags and large attachments to validate lazy loading effectiveness.

### Test Scenario
A complex task requiring:
- Multiple tags (10+)
- Large attachment files
- Many team members to choose from
- High data volume

### Input Data
```json
{
  "task_title": "Launch new product feature",
  "task_description": "Coordinate cross-functional launch for the new analytics dashboard",
  "assignee": "sarah.smith@company.com",
  "due_date": "2025-12-01",
  "priority": "critical",
  "tags": ["product", "launch", "analytics", "dashboard", "cross-functional", 
           "marketing", "engineering", "design", "qa", "docs"],
  "attachments": ["requirements.pdf", "mockups.zip", "data_model.xlsx"]
}
```

### Environment Configuration
```json
{
  "network_latency_ms": 100,
  "tag_count": 50,
  "member_count": 25,
  "attachment_size_kb": 5000
}
```

### Expected Metrics
- **Modal Load Time**: ≤800ms (pre), ≤300ms (post)
- **Lazy Loading Triggered**: Not applicable (pre), true (post)
- **Tags Loaded After Step 1**: false (pre - eager), true (post)
- **Task Create Time**: ≤5000ms

### Pass Criteria
- [x] Modal opens despite heavy data
- [x] Tags loaded after Step 1 (post-improvement only)
- [x] Attachments loaded after Step 2 (post-improvement only)
- [x] Task created successfully

### What This Tests
- Performance under load
- Lazy loading effectiveness
- Scalability of wizard approach
- Heavy data handling

---

## TC003: Slow Network Simulation

### Description
Simulates 3G network conditions to verify perceived performance improvements.

### Test Scenario
User on slow connection (3G, satellite, congested network):
- 500ms base latency
- Moderate data volumes
- Tests progressive enhancement

### Input Data
```json
{
  "task_title": "Update security protocols",
  "task_description": "Review and update company-wide security protocols",
  "assignee": "mike.jones@company.com",
  "due_date": "2025-11-20",
  "priority": "medium",
  "tags": ["security", "compliance"],
  "attachments": ["security_audit.pdf"]
}
```

### Environment Configuration
```json
{
  "network_latency_ms": 500,
  "tag_count": 30,
  "member_count": 15,
  "attachment_size_kb": 2000
}
```

### Expected Metrics
- **Modal Load Time**: ≤1500ms (pre), ≤800ms (post)
- **Time to Title Visible**: ≤800ms (post - critical improvement)
- **Progressive Loading Visible**: true (post)
- **User Can Start Typing Immediately**: false (pre), true (post)

### Pass Criteria
- [x] Modal opens (not timeout)
- [x] User can start typing immediately (post)
- [x] Loading indicators shown
- [x] Task created successfully
- [x] No timeout errors

### What This Tests
- Performance on poor networks
- Progressive enhancement effectiveness
- User experience under adverse conditions
- Perceived performance improvements

---

## TC004: Malformed Input & Validation

### Description
Tests error handling with invalid and missing required fields.

### Test Scenario
User makes mistakes:
- Forgets required fields
- Enters invalid data formats
- Provides malformed inputs

### Input Data
```json
{
  "task_title": "",
  "task_description": "This task has no title and invalid due date",
  "assignee": "invalid-email",
  "due_date": "not-a-date",
  "priority": "ultra-mega-high",
  "tags": [12345, null, "valid-tag"],
  "attachments": ["file_without_extension"]
}
```

### Environment Configuration
```json
{
  "network_latency_ms": 50,
  "tag_count": 10,
  "member_count": 5,
  "attachment_size_kb": 100
}
```

### Expected Metrics
- **Validation Errors Shown**: true
- **Title Error Visible**: true
- **Due Date Error Visible**: true
- **Assignee Error Visible**: true
- **Success**: false (expected - validation should prevent submission)

### Pass Criteria
- [x] Modal opens
- [x] Validation prevents submission
- [x] Error messages are clear
- [x] No crashes
- [x] User can correct errors

### What This Tests
- Validation logic
- Error message clarity
- Graceful error handling
- User recovery path
- Edge case robustness

---

## TC005: Accessibility & Keyboard Navigation

### Description
Validates keyboard-only navigation and screen reader compatibility.

### Test Scenario
User with accessibility needs:
- Uses keyboard only (no mouse)
- Uses screen reader
- Requires ARIA support

### Input Data
```json
{
  "task_title": "Accessibility audit",
  "task_description": "Conduct full accessibility audit of the platform",
  "assignee": "emily.chen@company.com",
  "due_date": "2025-11-25",
  "priority": "high",
  "tags": ["accessibility", "a11y", "compliance"],
  "attachments": []
}
```

### Environment Configuration
```json
{
  "network_latency_ms": 50,
  "tag_count": 10,
  "member_count": 5,
  "attachment_size_kb": 0,
  "keyboard_only": true,
  "screen_reader_mode": true
}
```

### Expected Metrics
- **All Fields Keyboard Accessible**: true
- **Tab Order Logical**: true
- **ARIA Labels Present**: true
- **Focus Indicators Visible**: true

### Pass Criteria
- [x] Modal opens via keyboard (Enter on button)
- [x] Can navigate all fields via Tab
- [x] Can submit via Enter
- [x] Can cancel via Escape
- [x] ARIA live regions announce changes
- [x] Task created successfully

### What This Tests
- WCAG 2.1 compliance
- Keyboard navigation
- ARIA attribute presence
- Screen reader compatibility
- Focus management
- Inclusive design

---

## Comparison Metrics

### Performance Metrics

| Metric | Pre (Typical) | Post (Typical) | Improvement |
|--------|---------------|----------------|-------------|
| Modal Load Time | 800-1200ms | 80-150ms | 60-85% ⬆️ |
| Time to Title Visible | 800-1200ms | 50-100ms | 80-90% ⬆️ |
| Task Create Time | 2000-4000ms | 1500-2500ms | 25-40% ⬆️ |

### UX Metrics

| Metric | Pre | Post | Status |
|--------|-----|------|--------|
| Title Visible w/o Scroll | ❌ false | ✅ true | Fixed |
| Auto-focus on Title | ❌ | ✅ | Added |
| Progressive Loading | ❌ | ✅ | Added |
| Wizard Flow | ❌ | ✅ | Added |

### Accessibility Metrics

| Metric | Pre | Post | Status |
|--------|-----|------|--------|
| ARIA Labels | Basic | Complete | ✅ |
| Keyboard Navigation | Partial | Full | ✅ |
| Screen Reader Support | Basic | Enhanced | ✅ |
| Focus Management | Poor | Excellent | ✅ |

---

## Test Execution Flow

### Pre-Improvement (Project A)
```
1. Open modal (wait for ALL data to load)
2. Scroll to find title field
3. Fill form fields (scattered)
4. Submit
5. Check for errors
```

### Post-Improvement (Project B)
```
1. Open modal (instant - Step 1 ready)
2. Title field auto-focused
3. Fill Step 1 (critical fields)
4. Click Next (lazy load Step 2)
5. Fill Step 2 (optional fields)
6. Click Next (lazy load Step 3)
7. Review summary in Step 3
8. Submit
```

---

## Success Thresholds

### Performance Thresholds (from test_data.json)
```json
{
  "performance_thresholds": {
    "modal_load_improvement_percent": 30,
    "task_create_improvement_percent": 20,
    "first_field_visibility_percent": 95,
    "acceptable_error_rate_percent": 5
  }
}
```

### Interpretation
- **Modal Load**: Must improve by ≥30% (typical: 60-85%)
- **Task Create**: Must improve by ≥20% (typical: 25-40%)
- **Field Visibility**: ≥95% of users see title immediately
- **Error Rate**: ≤5% of operations fail

---

## Screenshot Artifacts

Each test case generates multiple screenshots:

### Pre-Improvement
- `screenshots_pre_{test_id}_initial.png` - Before modal
- `screenshots_pre_{test_id}_modal_open.png` - Modal loaded
- `screenshots_pre_{test_id}_success.png` - Task created
- `screenshots_pre_{test_id}_error.png` - On failure
- `screenshots_pre_{test_id}_validation.png` - Validation errors

### Post-Improvement
- `screenshots_post_{test_id}_initial.png` - Before modal
- `screenshots_post_{test_id}_step1.png` - Wizard Step 1
- `screenshots_post_{test_id}_step1_filled.png` - Step 1 filled
- `screenshots_post_{test_id}_step2.png` - Wizard Step 2
- `screenshots_post_{test_id}_step3_summary.png` - Step 3 with summary
- `screenshots_post_{test_id}_success.png` - Task created

---

## Log Files

### log_pre.txt
Contains detailed execution logs for pre-improvement tests:
- Timestamps for each operation
- Performance metrics
- Error messages
- Test pass/fail status

### log_post.txt
Contains detailed execution logs for post-improvement tests:
- Timestamps for each operation
- Wizard step transitions
- Lazy loading timings
- Performance metrics

---

## Results JSON Schema

### results_pre.json / results_post.json
```json
{
  "project": "Project A/B",
  "timestamp": "ISO 8601 timestamp",
  "total_tests": 5,
  "passed": 4,
  "failed": 1,
  "results": [
    {
      "test_id": "TC001_normal_task",
      "description": "...",
      "timestamp": "...",
      "passed": true,
      "metrics": {
        "modal_load_time_ms": 123.45,
        "time_to_title_visible_ms": 67.89,
        "task_create_time_ms": 2345.67,
        "title_visible_without_scroll": true,
        "success": true
      },
      "errors": [],
      "screenshots": ["path1.png", "path2.png"]
    }
  ]
}
```

---

## Running Individual Test Cases

To run a specific test case, modify the test harness:

```python
# In test_pre_ui.py or test_post_ui.py
test_cases = [tc for tc in test_cases if tc['test_id'] == 'TC001_normal_task']
```

Or use test filtering in pytest (future enhancement).

---

**For full execution instructions, see QUICKSTART.md**
**For detailed documentation, see README.md**
