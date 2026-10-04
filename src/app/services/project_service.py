from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


async def get_project(db: AsyncSession, project_id: int, owner_id: int) -> Project:
    project = await db.get(Project, project_id)
    if project is None:
        raise NotFoundError(f"Project {project_id} not found")
    if project.owner_id != owner_id:
        raise ForbiddenError("You don't have access to this project")
    return project


async def list_projects(
    db: AsyncSession, owner_id: int, skip: int = 0, limit: int = 20
):
    query = select(Project).where(Project.owner_id == owner_id)
    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    result = await db.execute(query.offset(skip).limit(limit))
    projects = result.scalars().all()
    return list(projects), total


async def create_project(
    db: AsyncSession, data: ProjectCreate, owner_id: int
) -> Project:
    project = Project(name=data.name, owner_id=owner_id)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def update_project(
    db: AsyncSession, project_id: int, data: ProjectUpdate, owner_id: int
) -> Project:
    project = await get_project(db, project_id, owner_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    await db.commit()
    await db.refresh(project)
    return project


async def delete_project(db: AsyncSession, project_id: int, owner_id: int) -> None:
    project = await get_project(db, project_id, owner_id)
    await db.delete(project)
    await db.commit()
