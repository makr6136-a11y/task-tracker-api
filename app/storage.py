from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

_tasks: dict[str, TaskResponse] = {}


def add_task(payload: TaskCreate) -> TaskResponse:
    """
    Create and persist a new task from a TaskCreate payload.

    Generates a new UUID id and sets created_at/updated_at to the
    current UTC time.

    Args:
        payload (TaskCreate): Validated task creation data.

    Returns:
        TaskResponse: The stored task.
    """
    now = datetime.now(timezone.utc)
    task = TaskResponse(
        id=str(uuid4()),
        title=payload.title,
        description=payload.description or "",
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        due_date=payload.due_date,
        created_at=now,
        updated_at=now,
    )
    _tasks[task.id] = task
    return task


def get_all_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
) -> list[TaskResponse]:
    """
    Return all stored tasks, optionally filtered by status and/or priority.

    Args:
        status (TaskStatus | None): If provided, only tasks with this
            exact status are included.
        priority (TaskPriority | None): If provided, only tasks with
            this exact priority are included.

    Returns:
        list[TaskResponse]: Matching tasks, in dict insertion order.
    """
    tasks = list(_tasks.values())
    if status is not None:
        tasks = [task for task in tasks if task.status == status]
    if priority is not None:
        tasks = [task for task in tasks if task.priority == priority]
    return tasks


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    """
    Look up a single task by id.

    Args:
        task_id (str): The task's unique id.

    Returns:
        TaskResponse | None: The matching task, or None if not found.
    """
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    """
    Apply a partial update to a stored task.

    Only fields explicitly set on `payload` are applied (via
    `model_dump(exclude_unset=True)`); `updated_at` is refreshed
    whenever there are updates to apply.

    Args:
        task_id (str): The task's unique id.
        payload (TaskUpdate): Fields to update.

    Returns:
        TaskResponse | None: The updated task; the unchanged existing
        task if `payload` has no fields set; or None if no task with
        `task_id` exists.
    """
    task = _tasks.get(task_id)
    if task is None:
        return None

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return task

    updated = task.model_copy(
        update={**updates, "updated_at": datetime.now(timezone.utc)}
    )
    _tasks[task_id] = updated
    return updated


def delete_task(task_id: str) -> bool:
    """
    Delete a stored task by id.

    Args:
        task_id (str): The task's unique id.

    Returns:
        bool: True if a task was deleted, False if no task with
        `task_id` existed.
    """
    if task_id not in _tasks:
        return False
    del _tasks[task_id]
    return True


def _reset() -> None:
    _tasks.clear()
