from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.task import TaskStatus
from app.schemas.pagination import PaginatedResponse
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=PaginatedResponse[TaskRead])
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: TaskStatus | None = None,
    project_id: int | None = None,
    db: Session = Depends(get_db),
):
    tasks, total = await task_service.list_tasks(db, skip, limit, status, project_id)
    return {"items": tasks, "total": total, "skip": skip, "limit": limit}


@router.post("", response_model=TaskRead, status_code=201)
async def create_task(data: TaskCreate, db: Session = Depends(get_db)):
    return await task_service.create_task(db, data)


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    return await task_service.get_task(db, task_id)


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db)):
    return await task_service.update_task(db, task_id, data)


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    await task_service.delete_task(db, task_id)
