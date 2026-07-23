# Verification Log

## Baseline Check (before any midterm changes)

Command: `python -m pytest tests/ -v`

Result: **21 passed** (0 failed)

This confirms the existing Task Tracker (Modules 1-3: CRUD endpoints, business rules, 21 existing tests) was fully working before any Feature 1/Feature 2 changes began.

---

## Feature 1: Due Dates + Overdue Filter

### Backend implementation summary
- Added `due_date: Optional[date] = None` to `TaskCreate`, `TaskUpdate`, `TaskResponse`
- Found and fixed a bug: `storage.add_task()` was missing `due_date=payload.due_date` in its explicit field list, causing due dates to silently save as `null` on creation (PATCH was unaffected, since it uses `model_dump(exclude_unset=True)` generically)
- Added `is_overdue(task, today)` as a pure function in `app/filters.py`
- Added `overdue: bool | None = None` query parameter to `GET /tasks`, composing with existing `status`/`priority` filters

### Manual verification (4 scenarios, single test run)
| Scenario | Expected | Actual |
|---|---|---|
| Past due date, status ToDo | Appears in `?overdue=true` | ✅ Appeared |
| Future due date | Excluded from `?overdue=true` | ✅ Excluded |
| Past due date, status Done | Excluded from `?overdue=true` | ✅ Excluded |
| No due date | Excluded from `?overdue=true` | ✅ Excluded |
| No filter applied | All 4 tasks returned | ✅ All 4 returned |

### Pytest results
Command: `python -m pytest tests/ -v`

Result: **31 passed** (21 baseline + 5 due-date tests + 5 overdue-filter tests)

New tests added:
- `test_create_task_with_valid_due_date_returns_201`
- `test_create_task_without_due_date_returns_201_with_null_due_date`
- `test_create_task_invalid_due_date_format_returns_422`
- `test_patch_update_due_date_returns_200`
- `test_patch_clear_due_date_returns_200_with_null`
- `test_overdue_filter_returns_task_with_past_due_date_and_not_done`
- `test_overdue_filter_excludes_task_with_future_due_date`
- `test_overdue_filter_excludes_done_task_even_with_past_due_date`
- `test_overdue_filter_excludes_task_with_no_due_date`
- `test_list_tasks_without_overdue_param_returns_all_tasks`

### Break Test evidence (Feature 1)
**Break introduced:** Commented out the `if task.status == TaskStatus.DONE: return False` check inside `is_overdue()` in `app/filters.py`.

**Result:** `test_overdue_filter_excludes_done_task_even_with_past_due_date` FAILED with `AssertionError: assert [{'due_date': '2020-01-01', ...}] == []` — the Done task incorrectly appeared as overdue once the check was removed. All other 30 tests remained unaffected.

**Conclusion:** This confirms the test precisely and correctly protects the "Done tasks are never overdue" business rule. The check was restored, and the suite returned to 31/31 passing.

---

## Feature 2: Search + Combined Filters

*(To be completed after Feature 2 implementation)*

---

## Full Behavior Contract (post both features)

*(To be completed after both features and any refactor)*

---

## Manual Browser / Frontend Checks

*(To be completed after frontend integration)*