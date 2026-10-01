from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


def get_task(db: Session, task_id: int) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise NotFoundError(f"Task {task_id} not found")
    return task


def list_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    status: TaskStatus | None = None,
    project_id: int | None = None,
) -> tuple[list[Task], int]:
    query = select(Task)
    if status is not None:
        query = query.where(Task.status == status)
    if project_id is not None:
        query = query.where(Task.project_id == project_id)

    total = db.scalar(select(func.count()).select_from(query.subquery()))
    tasks = db.scalars(query.offset(skip).limit(limit)).all()
    return list(tasks), total


def create_task(db: Session, data: TaskCreate) -> Task:
    task = Task(**data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task_id: int, data: TaskUpdate) -> Task:
    task = get_task(db, task_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int) -> None:
    task = get_task(db, task_id)
    db.delete(task)
    db.commit()
