from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.project import Project
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


async def get_task(db: AsyncSession, task_id: int, owner_id: int) -> Task:
    task = await db.get(Task, task_id)
    if task is None:
        raise NotFoundError(f"Task {task_id} not found")
    if task.project.owner_id != owner_id:
        raise ForbiddenError("You don't have access to this task")
    return task


async def list_tasks(
    db: AsyncSession,
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

    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    result = await db.execute(query.offset(skip).limit(limit))
    tasks = result.scalars().all()
    return list(tasks), total


async def create_task(db: AsyncSession, data: TaskCreate, owner_id: int) -> Task:
    project = await db.get(Project, data.project_id)
    if project is None:
        raise NotFoundError(f"Project {data.project_id} not found")
    if project.owner_id != owner_id:
        raise ForbiddenError("You don't own this project")

    task = Task(**data.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def update_task(
    db: AsyncSession, task_id: int, data: TaskUpdate, owner_id: int
) -> Task:
    task = await get_task(db, task_id, owner_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task_id: int, owner_id: int) -> None:
    task = await get_task(db, task_id, owner_id)
    await db.delete(task)
    await db.commit()
