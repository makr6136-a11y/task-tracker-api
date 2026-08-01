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


def matches_keyword(task: TaskResponse, term: str) -> bool:
    """
    Determine whether a task matches a search keyword.

    Args:
        task (TaskResponse): The task to check.
        term (str): The search term to match against title and description.

    Returns:
        bool: True if the term is empty or appears in the task title or
            description (case-insensitive), otherwise False.
    """
    if term.strip() == "":
        return True

    needle = term.strip().casefold()
    title = task.title.casefold()
    description = (task.description or "").casefold()
    return needle in title or needle in description
