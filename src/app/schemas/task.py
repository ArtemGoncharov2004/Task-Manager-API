from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


class TaskStatusShema(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskCreateShema(BaseModel):
    title: str = Field(min_leng=1, max_length=50)
    description: str | None = None
    status: TaskStatusShema = TaskStatusShema.TODO
    priority: int = Field(default=3, ge=1, le=5)


class TaskUpdateShema(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatusShema | None = None
    priority: int | None = Field(default=None, ge=1, le=5)


class TaskReadShema(TaskCreateShema):
    id: int
    created_at: datetime
