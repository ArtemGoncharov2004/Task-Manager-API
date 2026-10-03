from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.project import Project
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


def get_task(db: Session, task_id: int, owner_id: int) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise NotFoundError(f"Task {task_id} not found")
    if task.project.owner_id != owner_id:
        raise ForbiddenError("You don't have access to this task")
    return task


def list_tasks(
    db: Session,
    owner_id: int,
    skip: int = 0,
    limit: int = 20,
    status: TaskStatus | None = None,
    project_id: int | None = None,
):
    query = select(Task).join(Project).where(Project.owner_id == owner_id)
    if status is not None:
        query = query.where(Task.status == status)
    if project_id is not None:
        query = query.where(Task.project_id == project_id)

    total = db.scalar(select(func.count()).select_from(query.subquery()))
    tasks = db.scalars(query.offset(skip).limit(limit)).all()
    return list(tasks), total


def create_task(db: Session, data: TaskCreate, owner_id: int) -> Task:
    project = db.get(Project, data.project_id)
    if project is None:
        raise NotFoundError(f"Project {data.project_id} not found")
    if project.owner_id != owner_id:
        raise ForbiddenError("You don't own this project")

    task = Task(**data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task_id: int, data: TaskUpdate, owner_id: int) -> Task:
    task = get_task(db, task_id, owner_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int, owner_id: int) -> None:
    task = get_task(db, task_id, owner_id)
    db.delete(task)
    db.commit()
