from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.pagination import PaginatedResponse
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services import project_service
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=PaginatedResponse[ProjectRead])
def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    projects, total = project_service.list_projects(db, current_user.id, skip, limit)
    return {"items": projects, "total": total, "skip": skip, "limit": limit}


@router.post("", response_model=ProjectRead, status_code=201)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_service.create_project(db, data, current_user.id)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_service.get_project(db, project_id, current_user.id)


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_service.update_project(db, project_id, data, current_user.id)


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project_service.delete_project(db, project_id, current_user.id)
