from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    owner_id: int
