# Task Tracker API (Module 1 Skeleton)

## Project Description

This is the initial project skeleton for the **Module 1 Task Tracker REST API**,
built with **Python** and **FastAPI**.

The chosen architecture (Option A) uses a lightweight backend built with
FastAPI, Pydantic, and JSON, favoring simplicity and ease of learning over
production-scale infrastructure. It is designed for beginners and
intermediate developers who want to focus on core API fundamentals without
the added complexity of databases, authentication, or deployment tooling.

The application runs locally with a single command and requires no external
services. API behavior can be tested easily using FastAPI's `TestClient`.

**Current scope of this skeleton:**
- FastAPI application instance
- A single `GET /health` endpoint for verifying the service is running

**Not yet included (by design, to be added in later modules):**
- Task CRUD endpoints
- Authentication / user accounts
- Database persistence (data will be in-memory when implemented)
- Docker / cloud deployment
- Frontend files
- Notifications or real-time updates

### Known limitations of this architecture

Because task data will be stored in memory once CRUD endpoints are added:
- All tasks will be lost whenever the server restarts.
- In-memory storage has limited scalability and may become harder to
  maintain as the application grows.

## Project Structure

```
task-tracker-api/
├── app/
│   ├── __init__.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   └── test_health.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Setup Instructions

1. **Clone or copy the project** to your local machine and navigate into it:

   ```bash
   cd task-tracker-api
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate      # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   > **Note:** The versions pinned in `requirements.txt` were accurate at
   > the time this skeleton was written. After installing, run
   > `pip freeze` and update `requirements.txt` if you want to lock in the
   > exact versions actually installed in your environment.

4. **Create your local environment file:**

   ```bash
   cp .env.example .env
   ```

   Adjust `PORT` or `APP_ENV` in `.env` if needed.

## Running the Application

Start the development server with a single command:

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

## Testing the /health Endpoint

With the server running, test it using `curl`:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "timestamp": "2026-07-05T12:00:00.000000+00:00"
}
```

You can also run the automated tests with:

```bash
pytest
```

## Exploring the API with Swagger

FastAPI automatically generates interactive API documentation. With the
server running, open your browser to:

```
http://localhost:8000/docs
```

This provides a Swagger UI where you can view and try out the available
endpoints directly.
