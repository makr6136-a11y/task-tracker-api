# Prompt Log

## Feature 1: Due Dates + Overdue Filter

### Prompt 1: Add due_date field to models (weak vs. strong comparison)

**Weak prompt (considered, not run):**
"Add due date field for my project"

**Why it's weak:** No file references, no field name, no type, no mention of which models need it (TaskCreate/TaskUpdate/TaskResponse), no constraints on scope. The AI would have to guess the field name, the data type (string vs. date), which models to touch, whether it's required or optional, and whether to add any routes or logic in the same step — any of which could go a different direction than intended.

**Strong prompt actually used:**
You are a senior Python backend engineer. Add due date support to my existing FastAPI Task Tracker.
Context files: @app/models.py @app/storage.py @app/main.py
Task: Modify the existing Task models to support an optional due date field. Do NOT add any routes yet.
Exact specification:

In app/models.py, add to TaskCreate, TaskUpdate, and TaskResponse:
due_date: Optional[date] = None
(import date from datetime)
TaskUpdate already uses exclude_unset=True in storage.update_task — confirm due_date will correctly support "omitted vs explicitly null" without extra code.
In app/storage.py, confirm add_task and update_task pass due_date through correctly without modification.

HARD CONSTRAINTS:

DO NOT use SQLAlchemy, SQLModel, Alembic, a database, or an ORM.
DO NOT use Pydantic v1 syntax.
DO NOT include id, created_at, or updated_at in TaskCreate or TaskUpdate.
DO NOT create any new API routes in this step.
DO NOT add overdue computation logic yet.
DO NOT rewrite the whole file — only show the modified sections/diff.

Output only the modified sections of app/models.py, and a one-line confirmation of whether app/storage.py needs any change.

**What AI returned (strong version):** Correctly added `due_date: Optional[date] = None` to exactly the three specified models, imported `date` from `datetime`, and added no new routes. Stated: *"app/storage.py does not need any change; add_task already reads payload.due_date... update_task uses model_dump(exclude_unset=True) so omitted vs explicit null is handled correctly."*

**Accepted / edited / rejected:** Accepted the model changes as-is. **Rejected the storage claim** — manual curl testing showed `due_date` was silently saving as `null` on creation. Inspected `storage.add_task()` and found it builds `TaskResponse` using an explicit, hand-written field list that never included `due_date`, so the field was dropped despite Pydantic not raising any error (since `due_date` has a default). Manually added `due_date=payload.due_date` to the `TaskResponse(...)` construction inside `add_task`. `update_task` was confirmed correct as claimed, since it merges fields generically via `model_dump(exclude_unset=True)`.

**Lesson:** Even a well-specified strong prompt can produce a confidently wrong statement about existing code (the storage claim) — the fix here wasn't better prompting, it was manual verification (running the actual request and checking the actual response) rather than trusting the AI's stated reasoning.

---

### Prompt 2: Add is_overdue logic and overdue filter

**Prompt used:**
Add overdue detection to my existing FastAPI Task Tracker.
Context files: @app/main.py @app/models.py @app/storage.py
Create a new module and modify only the existing GET /tasks route.
============================================================
FILE 1 - app/filters.py
Use these imports:
from datetime import date
from app.models import TaskResponse, TaskStatus
Create this function:
def is_overdue(task: TaskResponse, today: date) -> bool:
if task.due_date is None:
return False
if task.status == TaskStatus.DONE:
return False
return task.due_date < today
============================================================
FILE 2 - app/main.py
Modify the existing GET /tasks route only.
Add this import if missing:
from datetime import date
from app.filters import is_overdue
GET /tasks behavior:

Add an optional query parameter: overdue: bool | None = None
After retrieving tasks from storage.get_all_tasks(status=status, priority=priority), if overdue is True, filter the results to only tasks where is_overdue(task, date.today()) is True.
If overdue is None or False, do not apply any overdue filtering.

DO NOT:

DO NOT store is_overdue as a persisted field.
DO NOT compute is_overdue inline in the route as an if/elif chain; use the is_overdue() function.
DO NOT modify POST, PATCH, or DELETE routes.
DO NOT change storage.py.
DO NOT add sorting by due date.

Output two code blocks:
FILE: app/filters.py
MODIFIED GET /tasks ROUTE ONLY FROM app/main.py

**What AI returned:** Correctly generated `is_overdue(task, today)` with the exact logic specified (null due date → false, Done status → false, otherwise compare to today), and correctly modified `list_tasks()` to add the `overdue` query param and apply filtering only when `overdue` is truthy.

**Accepted / edited / rejected:** Accepted the logic as-is after manual verification (created 4 test tasks covering all overdue/non-overdue combinations, confirmed the filter returned exactly the correct subset). **Manually edited** one side effect: the edit introduced a duplicate `from datetime import ...` line in `app/main.py` (one pre-existing, one newly added) — manually removed the redundant shorter line, keeping only the merged import.

---

### Prompt 3: Generate pytest tests for due_date and overdue filter

**Prompt used:**
You are a senior Python developer writing pytest tests for a FastAPI app.
Context files: @app/main.py @app/models.py @app/storage.py @app/filters.py @tests/conftest.py @tests/test_tasks.py
Task: Add new tests to tests/test_tasks.py for the overdue filter. Do NOT modify existing tests.
Generate these named tests:

test_overdue_filter_returns_task_with_past_due_date_and_not_done
test_overdue_filter_excludes_task_with_future_due_date
test_overdue_filter_excludes_done_task_even_with_past_due_date
test_overdue_filter_excludes_task_with_no_due_date
test_list_tasks_without_overdue_param_returns_all_tasks

Use the existing client fixture from conftest.py. Do not use the created_task fixture for these tests since each test needs specific due_date/status combinations at creation time.
DO NOT:

DO NOT modify existing tests.
DO NOT change conftest.py.
DO NOT change app/filters.py or app/main.py.

Output only the new test functions to add to tests/test_tasks.py.

(A similar earlier prompt, using the same structure, was also used to generate the 5 due-date-specific tests: `test_create_task_with_valid_due_date_returns_201`, `test_create_task_without_due_date_returns_201_with_null_due_date`, `test_create_task_invalid_due_date_format_returns_422`, `test_patch_update_due_date_returns_200`, `test_patch_clear_due_date_returns_200_with_null`.)

**What AI returned:** 10 well-structured tests total (5 due-date + 5 overdue-filter) covering valid/invalid due dates, clearing a due date via PATCH, and all 4 overdue-filter scenarios (past-due, future, done-but-past-due, no-due-date) plus a no-filter sanity check.

**Accepted / edited / rejected:** Accepted all 10 tests as generated, after running the full suite and confirming 31/31 passed. Additionally ran a Break Test (commenting out the "Done tasks are never overdue" check in `is_overdue()`), which correctly caused exactly one test to fail (`test_overdue_filter_excludes_done_task_even_with_past_due_date`), confirming the tests are meaningful rather than superficially passing.

---

## Feature 2: Search + Combined Filters

*(To be completed after Feature 2 implementation)*