# AGENTS.md

Guidance for Codex and other AI coding agents working in this Task Tracker repository.

## 1. Project Summary

This repository contains a local Task Tracker application:

- A FastAPI REST API in `app/`.
- Pydantic request and response models in `app/models.py`.
- In-memory task storage in `app/storage.py`; there is no database or durable persistence.
- Status-transition rules in `app/business_rules.py`.
- An overdue-filter helper in `app/filters.py`.
- A single-file vanilla HTML/CSS/JavaScript frontend in `frontend/index.html`.
- A pytest suite in `tests/`.

The API currently defines:

- `GET /health`
- `GET /tasks`
- `POST /tasks`
- `GET /tasks/{task_id}`
- `PATCH /tasks/{task_id}`
- `DELETE /tasks/{task_id}`

`GET /tasks` accepts `status`, `priority`, and `overdue` query parameters.
Search and keyword filtering are not implemented on this branch. Search is
documented as a planned feature in `docs/midcourse/mini-adr.md`.

Sources: `README.md`, `app/main.py`, `app/storage.py`, `app/filters.py`, and `frontend/index.html`.

## 2. Tech Stack

Versions confirmed by `requirements.txt`:

- FastAPI 0.115.6
- Pydantic 2.10.3
- Uvicorn 0.32.1 with standard extras
- pytest 8.3.4
- httpx 0.28.1
- python-dotenv 1.0.1

Other confirmed components:

- Python application code
- Vanilla HTML, CSS, and JavaScript frontend
- In-memory Python dictionary storage
- Docker image based on `python:3.11-slim`
- GitHub Actions CI using Python 3.11 on Ubuntu

Python 3.11 is confirmed for the Docker image and CI workflow by `Dockerfile` and `.github/workflows/ci.yml`. The required local-development Python version is not confirmed by a dedicated version file.

There is no confirmed frontend package manager, framework, bundler, or build command.

Sources: `requirements.txt`, `Dockerfile`, `.github/workflows/ci.yml`, `frontend/index.html`, and `app/storage.py`.

## 3. Supported Setup, Run, and Test Commands

Run commands from the repository root.

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the API locally:

```bash
uvicorn app.main:app --reload --port 8000
```

Run the pytest suite:

```bash
pytest -v
```

`pytest.ini` sets `pythonpath = .`. `tests/conftest.py` creates a FastAPI `TestClient` and clears in-memory storage before and after each test.

The GitHub Actions workflow runs `pytest -v` after installing `requirements.txt` on Python 3.11 for pushes and pull requests.

Optional Docker commands documented by the repository:

```bash
docker build -t task-tracker-api .
docker run --rm -p 8000:8000 task-tracker-api
```

The frontend has no confirmed build command. It is a static `frontend/index.html` file that calls `http://localhost:8000`.

Do not claim that another setup, lint, formatting, migration, frontend build, deployment, or test command is supported unless repository evidence is found. Mark such commands as `not confirmed`.

Sources: `README.md`, `requirements.txt`, `pytest.ini`, `tests/conftest.py`, `.github/workflows/ci.yml`, `Dockerfile`, and `frontend/index.html`.

## 4. Architecture and Persistence

- `app/main.py` creates the FastAPI application, configures CORS, and defines the routes.
- `app/models.py` defines task status and priority enums plus create, update, and response models.
- `app/storage.py` stores tasks in the module-level `_tasks` dictionary.
- `app/business_rules.py` validates status changes.
- `app/filters.py` implements overdue detection. It does not implement keyword
  matching on this branch.
- `frontend/index.html` implements the browser interface and communicates with the API using `fetch`.
- `tests/` contains API and model behavior checks.

Storage is process-local and non-durable. Tasks are expected to be lost when the API process restarts. Do not describe this repository as database-backed.

Sources: `app/main.py`, `app/models.py`, `app/storage.py`, `app/business_rules.py`, `app/filters.py`, `frontend/index.html`, and `tests/`.

## 5. Business Rules

These rules are taken from the current code and tests.

### Statuses

Allowed `TaskStatus` values:

- `ToDo`
- `InProgress`
- `Done`

The default status for a newly created task is `ToDo`.

Source: `app/models.py`.

### Priorities

Allowed `TaskPriority` values:

- `Low`
- `Medium`
- `High`

The default priority for a newly created task is `Medium`.

Source: `app/models.py`.

### Status Transitions

The only permitted PATCH status transitions are:

- `ToDo` to `InProgress`
- `InProgress` to `Done`
- `Done` to `InProgress`

All other transitions are rejected with HTTP 422. This includes assigning the task its current status and moving directly from `ToDo` to `Done`.

Creation may set any valid status because transition validation is applied by the PATCH route, not the POST route.

Sources: `app/business_rules.py`, `app/main.py`, and `tests/test_tasks.py`.

### Task Validation and Defaults

For task creation:

- `title` is required.
- Leading and trailing title whitespace is removed.
- A blank or whitespace-only title is rejected.
- A title longer than 200 characters is rejected.
- `description` defaults to an empty string.
- `status` defaults to `ToDo`.
- `priority` defaults to `Medium`.
- `assignee` defaults to null.
- `due_date` defaults to null and uses a date value.
- Unknown request fields are forbidden.

For partial updates:

- Only explicitly supplied fields are changed.
- A supplied title follows the same trimming, nonblank, and 200-character rules.
- Unknown request fields are forbidden.
- `updated_at` is refreshed when at least one update is applied.

Sources: `app/models.py`, `app/storage.py`, and `tests/test_tasks.py`.

### IDs and Timestamps

- New task IDs are UUID strings generated by the server.
- `created_at` and `updated_at` are initialized from the current UTC time.
- Clients cannot set response-only fields such as `id` and `created_at` through the create or update models.

Sources: `app/models.py`, `app/storage.py`, `tests/test_tasks.py`, and `tests/verify_a.py`.

### Filters

- Status and priority filters use exact enum matches.
- A task is overdue only when it has a due date strictly before today and its status is not `Done`.
- The current route applies the overdue filter only when `overdue` is truthy. Therefore, `overdue=false` does not select non-overdue tasks.
- Search and keyword filtering are not implemented on this branch.

Sources: `app/main.py`, `app/storage.py`, `app/filters.py`, and `tests/test_tasks.py`.

## 6. Module 5 Working Guardrails

### Docs First

Before proposing work:

1. Read this `AGENTS.md`.
2. Read `README.md`.
3. Read documentation relevant to the requested task.
4. Inspect the affected implementation and tests before making claims or proposing edits.
5. Treat current executable code as the source of truth when older prose or metadata conflicts with it, and report the conflict.

### Read-Only by Default

- Begin with inspection and analysis only.
- Do not create, edit, delete, move, or rename files unless the user explicitly asks for a change.
- Do not run the app, tests, installation commands, Docker commands, or other state-changing commands unless the user authorizes that work.
- Read-only repository inspection is allowed when it is relevant to the request.
- State clearly whether commands were actually run or merely identified from repository evidence.

### One Task per Thread

- Keep each Codex thread focused on one concrete task.
- If a request introduces unrelated work, recommend handling it in a separate thread.
- Do not silently broaden the requested scope.

### Protect `app/`

- Do not modify any file under `app/` unless the user explicitly approves application-code changes.
- Approval to edit documentation, tests, frontend files, or configuration does not imply approval to edit `app/`.
- Before an approved `app/` change, cite the relevant current behavior and identify the exact files intended for modification.

## 7. Security and Governance

- Never paste, print, commit, or expose secrets, tokens, passwords, API keys, credentials, private keys, cookies, or sensitive environment values.
- Do not open or reproduce `.env` contents. Inspect `.env.example` only when configuration documentation is relevant.
- Never run destructive commands, including broad deletion, destructive Git resets, or commands that could overwrite unrelated user work.
- Preserve existing user changes and keep edits within the explicitly approved scope.
- Cite the exact repository files supporting technical claims.
- Separate confirmed facts from assumptions and mark unsupported details as `not confirmed`.
- Do not invent files, commands, test results, runtime behavior, requirements, vulnerabilities, or findings.
- Do not claim that a test passes unless it was actually run successfully during the current task.
- Do not claim production readiness, authentication, database persistence, deployment support, or security guarantees without direct repository evidence.
- If documentation and code disagree, cite both and explain the discrepancy instead of choosing silently.
- Avoid exposing repository content that is unrelated to the user's task.

## 8. Known Items Requiring Care

- The user identifies this as Module 5, while `README.md` labels the project Module 4 and metadata/docstrings in `app/main.py` still mention Module 1. The authoritative module label is not confirmed by consistent repository evidence.
- `Dockerfile` and `.github/workflows/ci.yml` confirm Python 3.11 for the container and CI, but a required local Python version is not confirmed by a dedicated version file.
- `python-dotenv` is installed, but application use of `.env` values is not confirmed in the inspected `app/` code.
- `.github/workflows/ci.yml` defines a test job for pushes and pull requests using Python 3.11, `requirements.txt`, and `pytest -v`.
- There is no confirmed linting or formatting command.
- There is no confirmed frontend build command.
- There is no confirmed database, authentication system, or durable persistence layer.

When evidence is missing or inconsistent, report `not confirmed` and ask for clarification when it materially affects the task.
