# Final AI Review — app/ and frontend/ Changes

## Change 1: SEC-05 — Priority payload fix

**File changed:** `frontend/index.html`

**What changed:** The task creation/edit payload previously always included a `priority` key, sending `priority: ""` when the user selected "(none)" in the priority dropdown. This is now conditional — `priority` is only added to the payload when a real value was selected.

**Why this qualifies as an allowed change:** This is a bug fix identified during the Module 5 security review (`docs/security-review.md`, finding SEC-05), not a new feature. Selecting "(none)" for priority previously caused the backend's `TaskPriority` enum validation to reject the request with `422`, instead of letting the backend's documented `Medium` default apply.

**Evidence this was reviewed, not blindly accepted:**
- The bug was first flagged by an AI-generated security review (Codex), grading it as `Low` severity.
- I independently verified the actual frontend code (`Select-String -Path frontend\index.html -Pattern "priorityVal"`) to confirm the exact mechanism before accepting the finding as real.
- The fix itself was AI-drafted (Copilot), shown as a diff, and reviewed line by line before being applied.
- The fix was tested live: creating a task with "(none)" priority selected now saves successfully and the resulting card correctly shows `Medium`, confirmed via the running frontend and a `201 Created` response in the backend log (previously a `422`).
- Full documentation of this finding, its grading, and the fix is in `docs/security-review.md` (finding SEC-05) and `docs/ai-usage.md`.

**Ownership statement:** I can explain every line of this change. It is a 5-line diff: removing `priority` from the unconditional payload object, and adding a 3-line conditional block that only sets `payload.priority` when `priorityVal` is not an empty string.

## No other app/ or frontend/ changes were made in this final round.

All other work in this final pass was documentation, branch consolidation (merging `mid-course-project`'s search feature into `main` before branching `final-project`), and verification (re-running the full test suite and a fresh Docker build/run/health-check cycle) — no other application logic was modified.