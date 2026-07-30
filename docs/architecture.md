# Task Tracker Architecture — Context Strategy Comparison

## Method (Module 5, Part 5.5)

The same architecture-documentation task was run three times with three different context strategies, to test the tradeoff between completeness and verifiability:

- **Strategy A — Minimal context:** Codex explored the repo freely with only a bare task description.
- **Strategy B — Structured context:** Codex was given `AGENTS.md` plus a pre-written file summary list, and read no files itself.
- **Strategy C — Targeted context:** Codex was restricted to exactly three anchor files (`app/main.py`, `app/models.py`, `app/storage.py`) and instructed to explicitly mark anything outside them as "not visible from the files I read."

## Strategy Comparison

| Strategy | What it got right | What it got wrong, missed, or invented | Best-suited task shape |
|---|---|---|---|
| **A — Minimal context** | Most complete end-to-end narrative (UI, API, storage, tests, business rules, user-visible errors); backend model and creation flow agree closely with B and C. | States specific frontend behavior (modal handling, validation messages, refetch, hard-coded API URL) and exact transition/test/CORS details without marking uncertainty — highest risk of invention since it doesn't distinguish observed fact from extrapolation. | Fast reconnaissance or a provisional overview where completeness matters more than auditability, and every claim will be verified later. |
| **B — Structured context** | Broadest repository-level coverage (backend, frontend, tests, Docker, CI); correctly captured a real nuance A and C missed (creation can set any valid status; transition rules only apply on later PATCH). | Made exact claims about Docker/CI/transitions/overdue logic/search/module metadata that can't be checked from the draft alone; internally inconsistent — names a Dockerfile and CI workflow in Key Files, then calls production deployment support "unconfirmed." | Repository-wide orientation or impact analysis needing coverage across many subsystems without reading every implementation file. |
| **C — Targeted context** | Strongest traceability — model, POST flow, validation, storage, timestamps, HTTP 201 all tied directly to the three inspected files; explicitly marked business rules, overdue logic, frontend, and tests as "not visible" instead of guessing. | Covers only the backend slice — misses frontend, tests, Docker/CI, exact transitions, and overdue semantics found in A/B; "Key files" lists 2 files that were referenced but never actually opened. | Focused documentation or implementation/review work where the relevant subsystem is known and every statement must be directly source-backed. |

## Verdict

Strategy C was chosen for the final architecture document. It offers the best evidentiary discipline: its central claims about the API, models, validation, request flow, and storage are grounded in actually-inspected files, while unverified areas are explicitly labeled rather than filled in with plausible-sounding guesses. Strategy B is more comprehensive and useful as a checklist for follow-up investigation, but its additional frontend, test, Docker, CI, and business-rule claims should not be promoted into a final document until independently verified against the underlying files.

## Context-Engineering Rule

For a focused architecture task with known implementation anchors, targeted context (Strategy C) is used because it produces source-traceable claims and exposes the boundary of what was not inspected. For a repository-wide discovery or planning task, structured context (Strategy B) is used instead because it surfaces more subsystems efficiently — but any summary-derived claim is then verified against the relevant files before being treated as architectural fact.

---

## Final Architecture Document (Strategy C, verified)

### 1. What the app does

The Task Tracker is a FastAPI REST service for creating, listing, retrieving, partially updating, and deleting tasks. It supports filtering by status, priority, and overdue state, plus a health-check endpoint and CORS access for configured local frontend origins.

### 2. Data model

The central entity is `Task`, represented through three Pydantic models:

- `TaskCreate`: title, description, status, priority, assignee, and due date.
- `TaskUpdate`: optional versions of all editable task fields for partial updates.
- `TaskResponse`: editable fields plus UUID string `id`, `created_at`, and `updated_at`.
- Status values: `ToDo`, `InProgress`, and `Done`.
- Priority values: `Low`, `Medium`, and `High`.

Defaults are an empty description, `ToDo` status, and `Medium` priority.

### 3. Request flow

When a client sends `POST /tasks`, FastAPI parses the body as `TaskCreate`. Pydantic rejects unknown fields, validates enum/date types, trims the title, and rejects blank or over-200-character titles. The endpoint passes the validated payload to `storage.add_task`, which generates a UUID, sets UTC creation and update timestamps, builds a `TaskResponse`, stores it in the process-local task dictionary, and returns it with HTTP 201.

### 4. Key files

- `app/main.py` — Configures FastAPI, CORS, health checks, CRUD routes, filters, and HTTP errors.
- `app/models.py` — Defines task schemas, enums, defaults, and title validation.
- `app/storage.py` — Implements in-memory CRUD operations and identifier/timestamp generation.
- `app/business_rules.py` — Referenced for validating status transitions; implementation is not visible from the files I read.
- `app/filters.py` — Referenced for overdue detection; implementation is not visible from the files I read.

### 5. Conventions

- Validation: Pydantic models forbid extra fields; titles are stripped and constrained to 1-200 nonblank characters; status and priority use enums.
- Storage: Tasks are held in a module-level dictionary keyed by UUID strings. Data is process-local and non-durable.
- Error handling: Missing resources produce `HTTPException` 404 responses. Invalid request data is handled through FastAPI/Pydantic; the precise response structure is not visible from the files I read. Invalid status transitions are documented as HTTP 422.
- Frontend/backend interaction: The backend exposes JSON REST endpoints and permits CORS from selected localhost development origins. The frontend implementation and its API-calling behavior are not visible from the files I read.

### 6. Not visible or assumptions

Authentication, authorization, database integration, deployment topology, concurrency strategy, automated tests, frontend architecture, and production configuration are not visible from the files I read. Status-transition and overdue rules are imported, but their definitions are not visible from the files I read. No assumptions were made about those areas.

---

## Appendix: Strategy A Draft (minimal context)

### 1. What the app does

Task Tracker is a local task-management application with a vanilla JavaScript board and a FastAPI REST API. Users can create, view, filter, edit, move, and delete tasks; tasks are grouped by status and can carry priority, assignee, and due-date information.

### 2. Data model

The only persisted entity is Task:

- `id`: server-generated UUID string
- `title`: required, trimmed, nonblank, maximum 200 characters
- `description`: string; defaults to `""`
- `status`: `ToDo`, `InProgress`, or `Done`; defaults to `ToDo`
- `priority`: `Low`, `Medium`, or `High`; defaults to `Medium`
- `assignee`: optional string
- `due_date`: optional date
- `created_at`, `updated_at`: server-generated UTC timestamps

`TaskCreate` accepts creation fields, `TaskUpdate` supports partial updates, and `TaskResponse` adds server-managed identity and timestamps.

### 3. Request flow: creating a task

1. The browser modal trims the title, rejects an empty title, builds a JSON payload, and sends `POST /tasks` to `http://localhost:8000`.
2. FastAPI parses the body as `TaskCreate`; Pydantic applies defaults, validates types and title rules, and rejects unknown fields.
3. The route calls `storage.add_task()`.
4. Storage generates a UUID and UTC timestamps, creates a `TaskResponse`, and inserts it into the process-local `_tasks` dictionary.
5. The API returns `201 Created` with the complete task. The frontend closes the modal and fetches the task list again. Validation errors (`422`) are shown beside fields or in the modal banner; other failures receive a generic error message.

### 4. Key files

- `app/main.py` — FastAPI setup, CORS configuration, and health/task CRUD routes.
- `app/models.py` — Task schemas, status/priority enums, defaults, and title validation.
- `app/storage.py` — Process-local task dictionary and CRUD storage functions.
- `app/business_rules.py` — Allowed status transitions for task updates.
- `app/filters.py` — Computes whether a task is overdue.
- `frontend/index.html` — Complete static UI and direct `fetch` interaction with the API.
- `tests/test_tasks.py` — API tests covering CRUD, validation, transitions, and filtering.
- `tests/conftest.py` — Test client and automatic storage reset between tests.

### 5. Conventions

- Validation: Pydantic models forbid unknown fields. Titles are trimmed, required, and limited to 200 characters; enums and dates are type-checked. The frontend also performs a basic required-title check.
- Storage: Tasks live in a module-level Python dictionary. Storage is process-local, non-durable, and lost when the server restarts.
- Error handling: FastAPI/Pydantic returns `422` for invalid input; routes return `404` for missing IDs and `204` after deletion. Invalid PATCH status transitions also return `422`.
- Frontend/backend interaction: The static frontend uses JSON over `fetch` against a hard-coded local API URL. After successful creation or editing, it reloads the task list. CORS permits selected local development origins and `file://` pages.
- Business rules: PATCH permits only `ToDo → InProgress`, `InProgress → Done`, and `Done → InProgress`. Overdue status is computed during reads rather than stored.

### 6. Not visible or assumptions

Authentication, authorization, multiple users, database persistence, production deployment, and a frontend build system are not present. Concurrency behavior, cross-process consistency, API versioning, observability, and production configuration are not confirmed. The README calls this Module 4 while stale metadata in `app/main.py` says Module 1; the authoritative module label is therefore unclear.

## Appendix: Strategy B Draft (structured context)

### What the app does

Task Tracker is a local Kanban-style application for creating, viewing, updating, filtering, and deleting tasks. It consists of a FastAPI REST API and a single-file vanilla HTML/CSS/JavaScript frontend. Tasks are held in process-local memory and are lost when the API restarts.

### Data model

The central entity is a task with a server-generated UUID string, required title, description, status, priority, optional assignee, optional due date, and UTC `created_at` and `updated_at` timestamps. Status values are `ToDo`, `InProgress`, and `Done`; priority values are `Low`, `Medium`, and `High`. New tasks default to an empty description, `ToDo` status, `Medium` priority, and null assignee and due date.

### Request flow

When a user creates a task, `frontend/index.html` sends an HTTP request to `POST /tasks`. FastAPI parses the request with `TaskCreate`, rejects unknown or invalid fields, trims the title, and enforces its nonblank and 200-character limit. The route passes the validated data to the in-memory storage layer, which generates the task ID and timestamps and adds the task to the module-level dictionary. The API returns the created task using the response schema. Creation may specify any valid status; transition rules apply only to later status changes through `PATCH`.

### Key files

- `app/main.py` — Creates the FastAPI app, configures CORS, and defines health and task routes.
- `app/models.py` — Defines task request/response schemas, enums, defaults, and validation.
- `app/storage.py` — Provides process-local task persistence through a module-level dictionary.
- `app/business_rules.py` — Defines and validates permitted task status transitions.
- `app/filters.py` — Determines whether a task is overdue.
- `frontend/index.html` — Implements the no-build Kanban interface and calls the API with `fetch`.
- `tests/conftest.py` — Supplies the API test client and resets storage around each test.
- `tests/test_tasks.py` — Checks CRUD, validation, transitions, and overdue filtering.
- `Dockerfile` — Builds a Python 3.11 image that runs under a non-root user.
- `.github/workflows/ci.yml` — Runs `pytest -v` with Python 3.11 on pushes and pull requests.

### Conventions

Pydantic models forbid unknown fields and separate create, partial-update, and response data. Titles are trimmed and validated; PATCH changes only explicitly supplied fields and refreshes `updated_at` when an update is applied. Status transitions are limited to `ToDo → InProgress`, `InProgress → Done`, and `Done → InProgress`; invalid transitions return HTTP 422. Storage is non-durable and local to the API process. The frontend communicates directly with the backend through `fetch` at `http://localhost:8000`. Status and priority filters match exact enum values. A task is overdue only when its due date is before today and its status is not `Done`.

### Not visible or assumptions

Authentication, database persistence, production deployment support, and frontend build tooling are not confirmed. The required local Python version is not confirmed, although Docker and CI use Python 3.11. Search and keyword filtering are planned but not implemented. The authoritative project module number is inconsistent across repository documentation and metadata. Exact error-response bodies and the frontend's detailed user interactions were not established from the supplied context.