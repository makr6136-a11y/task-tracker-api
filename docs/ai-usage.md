# AI Usage — Governance Retrospective (Module 5)

## Traced Code Block

Function traced: `update_task` in `app/storage.py`.

| Line(s) | What it does | Why it is there | What could break | Do I own this yet? |
|---|---|---|---|---|
| `def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:` | Defines a function that accepts a task ID and update payload, returning either a `TaskResponse` or `None`. | `Optional[TaskResponse]` communicates that "no matching task" is a normal, expected outcome. | Renaming/changing parameters would break callers. | Yes — confirmed via existing test coverage (`test_patch_not_found_returns_404`). |
| `task = _tasks.get(task_id)` | Looks up the task; `.get()` returns `None` instead of raising `KeyError` if missing. | Lets the next lines handle a missing task gracefully. | Using `_tasks[task_id]` instead would raise `KeyError` for unknown IDs. | Yes — `_tasks` confirmed to be a plain dict in `storage.py`. |
| `if task is None: return None` | Guard clause stopping early when no task is found. | Lets the rest of the function safely assume `task` exists. | Removing it would crash on `task.model_copy(...)` when `task` is `None`. | Yes. |
| `updates = payload.model_dump(exclude_unset=True)` | Converts the update model to a dict, including only explicitly supplied fields. | Distinguishes "field omitted" from "field explicitly set," critical for partial updates. | Removing `exclude_unset=True` would overwrite fields with model defaults. | Yes — confirmed via `test_patch_clear_due_date_returns_200_with_null`, which specifically tests this omitted-vs-explicit-null distinction. |
| `if not updates: return task` | Returns the unchanged task if no fields were actually supplied. | Avoids refreshing `updated_at` on a true no-op request. | Removing it would falsely record activity on empty updates. | Yes. |
| `updated = task.model_copy(update={**updates, "updated_at": datetime.now(timezone.utc)})` | Creates a new task object with the updates applied and `updated_at` refreshed server-side. | Server controls the timestamp, not the caller; avoids mutating the original object. | Reversing key order would let a caller override the server timestamp. | Yes — `datetime`/`timezone` usage confirmed correct throughout this project. |
| `_tasks[task_id] = updated` | Replaces the stored task with the updated version. | Makes the change visible to future lookups. | **Not thread-safe — this check-then-act pattern is the root cause of YOU-01, the race condition found in the independent security scan.** | **Partially — the logic is understood, but the concurrency risk it introduces was not fixed, only documented.** |
| `return updated` | Returns the new task to the caller. | Lets the caller confirm the update succeeded and see the new state. | Returning `task` instead would return stale data. | Yes. |

**Note:** This trace independently identified the same concurrency risk found separately during the manual security scan (`docs/security-review.md`, finding YOU-01) — a strong cross-check that this is a genuine, non-speculative issue.

## Three Personal AI Usage Rules

**1. Never paste:** I will never paste GitHub Personal Access Tokens, GitHub account-settings screenshots containing personal information, personal email addresses, or real user data into an AI chat or an AI-assisted terminal. I will use only test/fake data.

**2. Always verify:** Before accepting an AI code-review finding or implementation claim, I will check the named files directly, run a manual behavior test for the affected feature, and perform an independent check rather than treating a static AI review as complete.

**3. Record:** For every AI prompt whose output affects or is considered for my work, I will record the exact prompt, the AI's response, and whether I accepted, edited, or rejected it — with my reasoning — in `docs/midcourse/prompt-log.md`. I will record test and verification results in `docs/midcourse/verification.md` when I run them. I will record security-review findings in `docs/security-review.md`, grade each as Valid, False Positive, or Noise, and clearly separate AI findings from findings I discovered independently.