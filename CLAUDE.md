# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 1. Tech Stack

- Python [VERIFY] — repo evidence (`venv/pyvenv.cfg`) shows **3.12.10**, not 3.11 as originally specified. No file in this repo pins 3.11. Do not assert 3.11 without further evidence; confirm the course-mandated version before relying on either number.
- FastAPI 0.115.6
- Pydantic v2 (2.10.3)
- Uvicorn 0.32.1 (`uvicorn[standard]`)
- pytest 8.3.4
- httpx 0.28.1 (used as the test client transport for FastAPI's `TestClient`)
- python-dotenv 1.0.1
- Frontend: vanilla JavaScript, single static file (`frontend/index.html`) — no framework, no build step, no bundler.

## 2. Run Command

```bash
uvicorn app.main:app --reload --port 8000
```

## 3. Test Command

```bash
pytest -v
```

## 4. Architecture

- **Backend** (`app/`):
  - `app/main.py` — FastAPI app instance, CORS middleware, and all routes (`/health`, `GET/POST /tasks`, `GET/PATCH/DELETE /tasks/{task_id}`).
  - `app/models.py` — Pydantic schemas: `TaskCreate`, `TaskUpdate`, `TaskResponse`, `TaskStatus`, `TaskPriority`. All use `model_config = ConfigDict(extra="forbid")`, so unknown fields return 422.
  - `app/storage.py` — in-memory persistence; module-level `_tasks: dict[str, TaskResponse]`. `_reset()` clears it and is invoked by the autouse fixture in `tests/conftest.py` before/after every test.
  - `app/business_rules.py` — **task status transition rules live here** (see Business Rules below).
  - `app/filters.py` — pure query-composition helpers (currently `is_overdue(task, today)`), used by the `GET /tasks` route.
- **Frontend**: `frontend/index.html` — single-file vanilla JS app that calls the API directly via `fetch`.
- **Tests** (`tests/`):
  - `tests/conftest.py` — `client` fixture (`TestClient(app)`) and the autouse `_reset_storage` fixture.
  - `tests/test_health.py`, `tests/test_tasks.py` — pytest test suites.
  - `tests/verify_a.py` — an ad hoc manual verification script, not collected by pytest; run directly with `python tests/verify_a.py` if needed.
- `pytest.ini` sets `pythonpath = .`, so tests import `app` directly with no package install step.

## 5. Business Rules

Read directly from `app/business_rules.py` and `app/models.py` — not inferred.

**`TaskStatus` values** (`app/models.py`): `ToDo`, `InProgress`, `Done`.

**Valid status transitions** (`VALID_TRANSITIONS` in `app/business_rules.py`), enforced only in `PATCH /tasks/{task_id}` before the update is written:

| From | To |
|---|---|
| ToDo | InProgress |
| InProgress | Done |
| Done | InProgress |

Any `(current, new)` pair not in this table — including setting a status to its own current value — is rejected with `422 Unprocessable Entity` and a detail message listing the allowed transitions. This means, as implemented: `ToDo → Done` directly is **not allowed**, and there is no forward path out of `Done` other than back to `InProgress`.

## 6. UI States and CORS

**UI states** (`frontend/index.html`, board driven by `setBoardState(state, message)`):
- `loading` — shown while fetching tasks.
- `empty` — shown when the task list is empty.
- `error` — shown on fetch/update failure, with a retry affordance.
- `ready` — normal board view once tasks are loaded.
- The create/edit modal has its own error handling: a top `#modal-error-banner` for general/server errors and inline `.field-error` elements per field (title, description, assignee) for validation errors.

**CORS** (`app/main.py`): `CORSMiddleware` explicitly allow-lists frontend dev origins — `http://localhost:5500`, `http://127.0.0.1:5500`, `http://localhost:5173`, and `null` (for `file://` pages) — with `allow_credentials=False`. No wildcard origin is used; add new dev ports to this list rather than switching to `*`.

## 7. Do-Not Rules

- Do not add authentication / user accounts.
- Do not add a database or any persistence layer beyond the existing in-memory `_tasks` dict.
- Do not add deployment steps (Docker, cloud config, CI/CD).
- Do not make major UI changes (new pages, redesigns, new frameworks/build tooling) without asking first.

## Notes

- The `README.md` describes only the original Module 1 skeleton (`/health` only). The actual codebase has grown well beyond that (full task CRUD, business rules, due-date/overdue filtering) — treat the code, not the README, as the source of truth for current scope.
- `docs/midcourse/mini-adr.md` documents a `search` query param on `GET /tasks` (case-insensitive substring match on title/description) as a planned feature. As of the last read, it is **not present** in `app/main.py` or `app/filters.py` — verify current code before assuming it's implemented.
- `docs/midcourse/` also contains `user-stories.md`, `prompt-log.md`, and `verification.md` (a running log of manual test scenarios and break-test results per feature).
