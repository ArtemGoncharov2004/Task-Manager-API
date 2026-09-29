from datetime import datetime
from itertools import count

from fastapi import APIRouter, HTTPException, status

from app.schemas.task import TaskCreateShema, TaskReadShema, TaskUpdateShema

router = APIRouter(prefix="/tasks", tags=["tasks"])

_tasks: dict[int, TaskReadShema] = {}
_id_counter = count(1)


@router.get("", response_model=list[TaskReadShema])
def list_tasks():
    return list(_tasks.values())


@router.post("", response_model=TaskReadShema, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreateShema):
    task = TaskReadShema(
        id=next(_id_counter), created_at=datetime.utcnow(), **data.model_dump()
    )
    _tasks[task.id] = task
    return task


@router.get("/{task_id}", response_model=TaskReadShema)
def get_task(task_id: int):
    task = _tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskReadShema)
def update_task(task_id: int, data: TaskUpdateShema):
    task = _tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    updated = task.model_copy(update=data.model_dump(exclude_unset=True))
    _tasks[task_id] = updated
    return updated


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    if _tasks.pop(task_id, None) is None:
        raise HTTPException(status_code=404, detail="Task not found")
