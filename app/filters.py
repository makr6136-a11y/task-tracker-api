from datetime import date

from app.models import TaskResponse, TaskStatus


def is_overdue(task: TaskResponse, today: date) -> bool:
    if task.due_date is None:
        return False
    if task.status == TaskStatus.DONE:
        return False
    return task.due_date < today
