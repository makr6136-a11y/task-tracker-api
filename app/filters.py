from datetime import date

from app.models import TaskResponse, TaskStatus


def is_overdue(task: TaskResponse, today: date) -> bool:
    """
    Determine whether a task is overdue.

    Args:
        task (TaskResponse): The task to check.
        today (date): The date to compare `task.due_date` against.

    Returns:
        bool: True if `task.due_date` is set, `task.status` is not
        Done, and `task.due_date` is strictly before `today`. False
        otherwise.
    """
    if task.due_date is None:
        return False
    if task.status == TaskStatus.DONE:
        return False
    return task.due_date < today
