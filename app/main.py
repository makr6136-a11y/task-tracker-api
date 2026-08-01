"""
Module 1 Task Tracker API
--------------------------
Entry point for the FastAPI application.

This skeleton intentionally contains no task CRUD endpoints yet.
It only exposes a /health endpoint used to verify that the service
is running correctly.
"""

from datetime import date, datetime, timezone

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.business_rules import validate_status_transition
from app import storage
from app.filters import is_overdue, matches_keyword
from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

app = FastAPI(
    title="Task Tracker API",
    description="Module 1 Task Tracker REST API (skeleton) built with FastAPI.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5173",
        "null",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    """
    Health check endpoint.

    Returns the service status and current UTC timestamp, used to verify
    that the API process is running and reachable.

    Returns:
        dict: A mapping with:
            - status (str): Always "ok".
            - timestamp (str): Current UTC time in ISO 8601 format.

    Example:
        GET /health -> 200 {"status": "ok", "timestamp": "2026-07-25T12:00:00+00:00"}
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    overdue: bool | None = None,
    search: str | None = None,
) -> list[TaskResponse]:
    """
    List tasks, optionally filtered by status, priority, overdue state,
    and a search term against title/description.

    Args:
        status (TaskStatus | None): If provided, only tasks with this
            exact status are returned.
        priority (TaskPriority | None): If provided, only tasks with
            this exact priority are returned.
        overdue (bool | None): If truthy, results are further restricted
            to tasks for which `is_overdue` returns True (has a past
            due_date and status is not Done). [VERIFY] The check is
            `if overdue:`, so `overdue=False` is not distinguished from
            `overdue=None` — neither applies overdue filtering.
        search (str | None): If provided, only tasks whose title or
            description contains the search term case-insensitively are
            returned.

    Returns:
        list[TaskResponse]: Tasks matching the given filters, in
        storage insertion order.

    Example:
        GET /tasks?status=ToDo&priority=High&overdue=true&search=report
    """
    tasks = storage.get_all_tasks(status=status, priority=priority)
    # overdue=False and overdue=None both skip overdue filtering intentionally.
    # This preserves the current behavior while making the intent explicit.
    if overdue:
        tasks = [task for task in tasks if is_overdue(task, date.today())]
    # matches_keyword() treats an empty string as no filter, so we still
    # evaluate this branch when search is provided but empty.
    if search is not None:
        tasks = [task for task in tasks if matches_keyword(task, search)]
    return tasks


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    """
    Create a new task.

    Args:
        payload (TaskCreate): Task fields to create. Unknown fields are
            rejected with 422 (model_config extra="forbid").

    Returns:
        TaskResponse: The newly created task, including its generated
        id and created_at/updated_at timestamps.

    Example:
        POST /tasks {"title": "Write docs"} -> 201 TaskResponse
    """
    return storage.add_task(payload)


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    """
    Retrieve a single task by id.

    Args:
        task_id (str): The task's unique id.

    Returns:
        TaskResponse: The matching task.

    Raises:
        HTTPException: 404 if no task with `task_id` exists.

    Example:
        GET /tasks/{task_id} -> 200 TaskResponse | 404
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """
    Partially update a task, enforcing status transition rules.

    Args:
        task_id (str): The task's unique id.
        payload (TaskUpdate): Fields to update; unset fields are left
            unchanged. Unknown fields are rejected with 422.

    Returns:
        TaskResponse: The updated task.

    Raises:
        HTTPException: 404 if no task with `task_id` exists.
        HTTPException: 422 if `payload.status` is set and the transition
            from the task's current status to the new status is not in
            `VALID_TRANSITIONS` (see app/business_rules.py).

    Example:
        PATCH /tasks/{task_id} {"status": "InProgress"} -> 200 TaskResponse
    """
    existing = storage.get_task_by_id(task_id)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

    if payload.status is not None:
        validate_status_transition(existing.status, payload.status)

    updated = storage.update_task(task_id, payload)
    return updated


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: str) -> None:
    """
    Delete a task by id.

    Args:
        task_id (str): The task's unique id.

    Returns:
        None: Responds with 204 No Content on success.

    Raises:
        HTTPException: 404 if no task with `task_id` exists.

    Example:
        DELETE /tasks/{task_id} -> 204 | 404
    """
    deleted = storage.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return None
    