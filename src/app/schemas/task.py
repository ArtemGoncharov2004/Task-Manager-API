from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: int = Field(default=3, ge=1, le=5)
    project_id: int = Field(gt=0)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus | None = None
    priority: int | None = Field(default=None, ge=1, le=5)


class TaskRead(TaskCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
