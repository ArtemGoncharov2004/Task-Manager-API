from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


def get_project(db, project_id: int, owner_id: int) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise NotFoundError(f"Project {project_id} not found")
    if project.owner_id != owner_id:
        raise ForbiddenError("You don't have access to this project")
    return project


def list_projects(db, owner_id: int, skip: int = 0, limit: int = 20):
    query = db.query(Project).filter(Project.owner_id == owner_id)
    total = query.count()
    projects = query.offset(skip).limit(limit).all()
    return projects, total


def create_project(db, data: ProjectCreate, owner_id: int) -> Project:
    project = Project(name=data.name, owner_id=owner_id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update_project(db, project_id: int, data: ProjectUpdate, owner_id: int) -> Project:
    project = get_project(db, project_id, owner_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


def delete_project(db, project_id: int, owner_id: int) -> None:
    project = get_project(db, project_id, owner_id)
    db.delete(project)
    db.commit()
