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

### Backend implementation summary
- Added `matches_keyword(task, term)` as a pure function in `app/filters.py`
- Case-insensitive substring match (using `.casefold()`) against `title` and `description`
- Empty/whitespace search term returns `True` for all tasks (no filter applied)
- Added `search: str | None = None` query parameter to `GET /tasks`, composing with existing `status`, `priority`, and `overdue` filters

### Manual verification (4 scenarios, single test run)
| Scenario | Expected | Actual |
|---|---|---|
| `search=milk` matching a task titled "Buy milk" | Task appears in results | ✅ Appeared |
| `search=MILK` (different case) | Same task still appears | ✅ Appeared (case-insensitive confirmed) |
| `search=` (empty) | All tasks returned, no filtering | ✅ All tasks returned |
| `search=xyz123nonsense` (no match) | `200` with `[]`, not an error | ✅ Returned `[]` |

### Pytest results
Command: `python -m pytest tests/ -v`

Result: **37 passed** (31 from Feature 1 + 6 search tests)

New tests added:
- `test_search_matches_title_case_insensitive`
- `test_search_matches_description`
- `test_search_no_match_returns_200_and_empty_list`
- `test_search_empty_string_returns_all_tasks`
- `test_search_combined_with_status_filter`
- `test_search_combined_with_priority_filter`

### Break Test evidence (Feature 2)
**Break introduced:** Commented out the `description` half of the match condition inside `matches_keyword()` in `app/filters.py`, changing `return needle in title or needle in description` to `return needle in title` only.

**Result:** `test_search_matches_description` FAILED — a task matched only by its description content ("Grocery run" with description containing "eggs") was no longer found when searching "eggs". All other 36 tests remained unaffected.

**Conclusion:** This confirms the test precisely and correctly protects the "search matches description, not just title" requirement. The check was restored, and the suite returned to 37/37 passing.

---

## Full Behavior Contract (post both features)

Verified manually at http://localhost:5500, after a full restart of both backend and frontend, with fresh test data covering all scenarios.

| # | Behavior | Result |
|---|---|---|
| 1 | Three columns render with correct counts | ✅ PASS |
| 2 | Cards sort by priority within each column | ✅ PASS |
| 3 | Loading state appears before tasks load | ✅ PASS |
| 4 | Empty columns remain visible | ✅ PASS |
| 5 | Error state appears when backend is stopped | ✅ PASS |
| 6 | Valid drag sends PATCH and updates board | ✅ PASS |
| 7 | Invalid drag/422 reverts and shows message | ✅ PASS |
| 8 | New Task/Edit modal flows work, including blank-title validation | ✅ PASS |
| 9 | Due date + overdue badge display and update correctly | ✅ PASS |
| 10 | Search filters by title/description correctly, clears properly | ✅ PASS |

**Result: 10/10 passing.** Both new features (due dates/overdue filter, search) integrate correctly with all pre-existing Module 3 board behavior — no regressions introduced.

## Full Pytest Suite (post both features)

Command: `python -m pytest tests/ -v`

Result: **37 passed** (0 failed)

## Refactor (post-checkpoint)

**Change:** Added clarifying comments to the `overdue` and `search` filter conditions in `GET /tasks` (`app/main.py`), explaining the intentional behavior of each (why `overdue=False`/`None` are treated identically, and why `search`'s "is not None" check still works correctly for empty strings via `matches_keyword`'s internal handling). No logic was changed.

**Before:** 37 passed (see "Full Pytest Suite" above)

**After:** 37 passed — confirmed via `python -m pytest -v`, and spot-checked manually via `curl` on both `?overdue=true` and `?search=milk`, both returning identical results to before the refactor.

**Conclusion:** Behavior contract and full test suite remain unchanged after the refactor, confirming it was purely clarifying and introduced no regressions.

## Manual Browser / Frontend Checks

- Confirmed via backend terminal logs that all frontend actions (create, edit, drag, search) correctly trigger the expected HTTP requests (`POST /tasks` → 201, `PATCH /tasks/{id}` → 200, `GET /tasks?search=...` → 200).
- Confirmed search-while-typing works correctly (fires on every keystroke via the `input` event); results narrow and clear as expected. No debounce was added — this was evaluated as unnecessary UX polish, not a functional requirement, given it does not affect correctness and is outside the scope of the original user stories.
- Confirmed in-memory storage resets on server restart are expected behavior (documented architecture decision from Module 1), not a bug — verified by recreating test data after each restart during this testing session.