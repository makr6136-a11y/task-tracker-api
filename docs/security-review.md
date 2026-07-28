# Security Review — Module 5

## Review Method

1. Ran a read-only security audit prompt in Codex, covering input validation, authorization, data exposure, error handling, dependencies/CI/Docker, and CORS.
2. Graded each AI finding independently: Valid, False Positive, or Noise — verifying claims directly against the actual code rather than trusting severity/confidence labels as given.
3. Closed the AI output and performed an independent manual scan, focused on an area the AI review did not cover: concurrency safety of the in-memory storage layer.
4. Reconciled both sets of findings into Agreement / AI-only / You-only.

## AI Findings (Codex, graded)

| ID | Severity | Finding | Grade |
|---|---|---|---|
| SEC-01 | Medium | No authentication/authorization on any endpoint | Valid (documented, intentional course-scope decision) |
| SEC-02 | Medium | `description`/`assignee` have no length limit; `GET /tasks` has no pagination | Valid |
| SEC-03 | Medium | CORS allows `"null"` origin plus wildcard methods/headers | Valid |
| SEC-04 | Low | Frontend displays raw validation/error response bodies | Noise — backend has no stack traces or verbose internal errors to leak |
| SEC-05 | Low | Selecting "(none)" priority sends `priority: ""`, rejected with 422 instead of applying the `Medium` default | **Valid — real bug, fixed and verified live** |
| SEC-06 | Low | Docker/CI use mutable tags instead of pinned digests/SHAs | Noise — acceptable tradeoff for a learning project (see `docs/decisions/dockerfile-design.md`) |
| GOV-01 | Low | Documentation/branch drift around whether `search` is implemented | **Valid — but the AI's first diagnosis was backwards.** Initial claim was that README was stale; verification showed the opposite — `AGENTS.md` incorrectly said search was implemented, while README was correct. Root cause: search was built only on `mid-course-project` and never merged into `main`. Fixed by correcting `AGENTS.md`. |

## Manual Scan Findings (independent)

| ID | Severity | Finding | Grade |
|---|---|---|---|
| YOU-01 | Medium | `app/storage.py`'s `update_task` and `delete_task` use check-then-act patterns on the shared `_tasks` dict with no locking. FastAPI runs sync `def` route handlers in a thread pool, so concurrent requests to the same `task_id` can race — causing lost updates, or a deleted task being "resurrected" by a racing PATCH. | **Valid — not caught by the AI's static, read-only review; not yet fixed** |

## Reconciliation

| Agreement | AI-only | You-only |
|---|---|---|
| SEC-05 — Priority payload mismatch (Valid, fixed): AI identified it; confirmed through code review and live reproduction. | SEC-01 — No authentication (Valid, accepted scope) | YOU-01 — Shared-state race condition (Valid, open) |
| GOV-01 — Search documentation drift (Valid, fixed): both reviews identified a branch/documentation mismatch; verification established that `AGENTS.md`, not `README.md`, was stale. | SEC-02 — Unbounded strings and task listing (Valid, open) | — |
| — | SEC-03 — Permissive CORS configuration (Valid, open) | — |
| — | SEC-04 — Raw frontend errors (Noise) | — |
| — | SEC-06 — Mutable build/CI tags (Noise) | — |

## Observation

AI coverage was broad across validation, API exposure, CORS, frontend/backend contracts, documentation governance, and build configuration. It was strongest at visible boundaries but missed the deeper concurrency and state-integrity risk caused by unsynchronized in-memory storage.

## Top-3 Security Backlog

| Rank | Finding | Why it matters | Suggested owner | Next action |
|---|---|---|---|---|
| 1 | YOU-01: Race conditions in `update_task` and `delete_task` | Concurrent requests can lose updates or allow a racing PATCH to restore a task after deletion, compromising data integrity. | Backend | Define concurrency semantics, protect compound storage operations with appropriate synchronization, and add deterministic concurrent PATCH/DELETE tests. |
| 2 | SEC-02: Unbounded task content and list size | Unlimited description/assignee lengths, task count, and full-list responses can consume excessive memory and response capacity. | Backend | Set justified field-length limits, introduce pagination or a maximum result size, and add boundary tests. |
| 3 | SEC-03: `null` CORS origin and wildcard methods/headers | A sandboxed or local-file page can interact with the unauthenticated local API; wildcard permissions broaden the allowed request surface. | Backend / course-project owner | Confirm whether direct `file://` use remains required. If not, remove `"null"` and restrict methods and headers to those actually used by the frontend. |