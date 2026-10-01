from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.tag import TagCreate, TagRead
from app.services import tag_service

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagRead])
def list_tags(db: Session = Depends(get_db)):
    return tag_service.list_tags(db)


@router.post("", response_model=TagRead, status_code=201)
def create_tag(data: TagCreate, db: Session = Depends(get_db)):
    return tag_service.create_tag(db, data)


@router.get("/{tag_id}", response_model=TagRead)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    return tag_service.get_tag(db, tag_id)


@router.delete("/{tag_id}", status_code=204)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    tag_service.delete_tag(db, tag_id)
