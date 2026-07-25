# Task Tracker API (Module 4)

## 1. Project Overview

A REST API for tracking tasks, built with **FastAPI** + **Pydantic v2**, backed by
in-memory storage (no database). It supports full task CRUD, status-transition
business rules, due-date/overdue filtering, and priority/status filtering. A
single-file vanilla-JS frontend (`frontend/index.html`) calls the API directly
via `fetch` — no build step, no framework.

This project favors simplicity and learning over production-scale
infrastructure: everything runs locally with one command and requires no
external services.

**Current scope:**
- `GET /health` — service health check
- `GET /tasks` — list tasks, filterable by `status`, `priority`, `overdue`
- `POST /tasks` — create a task
- `GET /tasks/{task_id}` — fetch a single task
- `PATCH /tasks/{task_id}` — partially update a task, enforcing status
  transition rules (see [Project Conventions](#9-project-conventions-and-current-limitations))
- `DELETE /tasks/{task_id}` — delete a task

**Explicitly not included:**
- Authentication / user accounts
- A database or any persistence beyond the in-memory `_tasks` dict
- Deployment / production hosting configuration
- This README does not claim the app is production-ready.

[VERIFY] `docs/midcourse/mini-adr.md` documents a planned `search` query
parameter on `GET /tasks` (case-insensitive substring match on title/
description). As of this README, it is **not implemented** in `app/main.py`
or `app/filters.py` — do not rely on it until it ships.

## 2. Prerequisites

- **Python 3.11** — matches the version pinned in `Dockerfile` and
  `.github/workflows/ci.yml`. [VERIFY] The `venv/` checked into this working
  copy was created with Python 3.12.10; no file in the repo pins 3.11 as the
  required *local dev* version, so confirm the course-mandated version
  before relying on either number.
- `pip` (bundled with Python)
- Docker Desktop (or another Docker engine) — only needed for the
  [Run with Docker](#6-run-with-docker) section.
- Git

## 3. Local Setup

Run these commands from the repo root.

1. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate      # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create your local environment file:

   ```bash
   cp .env.example .env
   ```

   [VERIFY] `.env.example` sets `PORT` and `APP_ENV`, and `python-dotenv` is
   listed in `requirements.txt`, but no code under `app/` currently calls
   `load_dotenv()` or reads these values — as of this read, `.env` does not
   appear to affect app behavior. This step is included for parity with the
   original project setup; confirm before assuming it does anything.

## 4. Run the App Locally

From the repo root, with the virtual environment activated:

```bash
uvicorn app.main:app --reload --port 8000
```

The API is available at `http://localhost:8000`, with interactive Swagger
docs at `http://localhost:8000/docs`.

**Frontend (optional):** `frontend/index.html` is a static file with no
build step. Open it directly in a browser, or serve it with a tool like the
VS Code "Live Server" extension. `app/main.py` allow-lists CORS origins
`http://localhost:5500`, `http://127.0.0.1:5500`, `http://localhost:5173`,
and `null` (for `file://` pages) — use one of those origins/ports if you
serve the frontend rather than opening it as a bare file.

## 5. Run Tests

From the repo root, with the virtual environment activated:

```bash
pytest -v
```

`pytest.ini` sets `pythonpath = .`, so tests import `app` directly with no
package install step. Test storage is reset before/after every test via an
autouse fixture in `tests/conftest.py`.

`tests/verify_a.py` is an ad hoc manual verification script, not collected
by pytest; run it directly if needed:

```bash
python tests/verify_a.py
```

## 6. Run with Docker

From the repo root:

```bash
docker build -t task-tracker-api .
docker run --rm -p 8000:8000 task-tracker-api
```

The API is available at `http://localhost:8000` inside the container. The
image is a two-stage build (`python:3.11-slim`) that installs dependencies
into a virtualenv, copies only the `app/` package into the runtime stage,
and runs as a non-root `app` user. [VERIFY] There is no `docker-compose.yml`
or Dockerfile `HEALTHCHECK` in this repo as of this read — this is a plain
single-container build/run, not a deployment setup.

## 7. CI Workflow Summary

`.github/workflows/ci.yml` runs on every `push` and `pull_request`:

1. Checks out the repo (`actions/checkout@v4`).
2. Sets up Python 3.11 (`actions/setup-python@v5`).
3. Installs dependencies: `pip install -r requirements.txt`.
4. Runs the test suite: `pytest -v`.

There is a single `test` job on `ubuntu-latest`; no Docker build, lint, or
deploy step is currently part of CI.

## 8. Project Structure

```
task-tracker-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, CORS config, all routes
│   ├── models.py             # Pydantic schemas (TaskCreate/Update/Response, enums)
│   ├── storage.py            # in-memory persistence (module-level _tasks dict)
│   ├── business_rules.py     # status transition validation
│   └── filters.py            # pure query helpers (is_overdue)
├── frontend/
│   └── index.html            # static vanilla-JS UI, no build step
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # TestClient fixture + autouse storage reset
│   ├── test_health.py
│   ├── test_tasks.py
│   └── verify_a.py           # manual script, not run by pytest
├── docs/
│   └── midcourse/
│       ├── mini-adr.md       # architecture decisions (due dates, search)
│       ├── user-stories.md
│       ├── prompt-log.md
│       └── verification.md   # manual test/break-test log
├── Dockerfile
├── .dockerignore
├── .env.example
├── .gitignore
├── pytest.ini
├── README.md
├── CLAUDE.md
└── requirements.txt
```

## 9. Project Conventions and Current Limitations

**Conventions:**
- All request/response models use `model_config = ConfigDict(extra="forbid")`
  (`app/models.py`) — unknown fields in a request body return `422`.
- `TaskStatus` values: `ToDo`, `InProgress`, `Done`.
- Status transitions are restricted (`app/business_rules.py`,
  `VALID_TRANSITIONS`): `ToDo → InProgress`, `InProgress → Done`,
  `Done → InProgress`. Any other `(current, new)` pair — including
  `ToDo → Done` directly, or setting a status to its own current value — is
  rejected with `422` on `PATCH /tasks/{task_id}`.
- Overdue is computed on read, not stored: `is_overdue(task, today)` in
  `app/filters.py` returns `True` only when `due_date` is set, status is not
  `Done`, and `due_date` is strictly before `today`.
- CORS uses an explicit origin allow-list (see [Run the App Locally](#4-run-the-app-locally)) — no wildcard origin, `allow_credentials=False`.

**Current limitations:**
- **All data is in-memory** — every task is lost on server restart; there is
  no database or file persistence.
- **No authentication** — every endpoint is open to any caller.
- **No deployment/production configuration** — the Dockerfile and CI run
  tests only; neither implies this app is production-ready.
- [VERIFY] `GET /tasks?overdue=false` and `GET /tasks?overdue=` (omitted) are
  currently indistinguishable — the route only checks truthiness of
  `overdue`, so there is no way to explicitly request "not overdue" via this
  parameter.
- [VERIFY] The `search` parameter described in `docs/midcourse/mini-adr.md`
  is not implemented as of this read (see [Project Overview](#1-project-overview)).

## 10. Decisions and Notes

[VERIFY] No `docs/decisions/` directory exists in this repo as of this read.
The closest equivalent is `docs/midcourse/mini-adr.md`, a mini architecture
decision record covering the due-date/overdue-filter and search features:

- [`docs/midcourse/mini-adr.md`](docs/midcourse/mini-adr.md) — architecture
  decisions (due dates + overdue filter; planned search + combined filters)
- [`docs/midcourse/user-stories.md`](docs/midcourse/user-stories.md)
- [`docs/midcourse/prompt-log.md`](docs/midcourse/prompt-log.md)
- [`docs/midcourse/verification.md`](docs/midcourse/verification.md) — manual
  test / break-test log
