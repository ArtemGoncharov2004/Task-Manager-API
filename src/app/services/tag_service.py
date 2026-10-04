from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.tag import Tag
from app.schemas.tag import TagCreate


async def list_tags(db: AsyncSession) -> list[Tag]:
    result = await db.execute(select(Tag))
    return list(result.scalars().all())


async def create_tag(db: AsyncSession, data: TagCreate) -> Tag:
    tag = Tag(**data.model_dump())
    db.add(tag)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ConflictError(f"Tag '{data.name}' already exists")
    await db.refresh(tag)
    return tag


async def get_tag(db: AsyncSession, tag_id: int) -> Tag:
    tag = await db.get(Tag, tag_id)
    if tag is None:
        raise NotFoundError(f"Tag {tag_id} not found")
    return tag


async def delete_tag(db: AsyncSession, tag_id: int) -> None:
    tag = await get_tag(db, tag_id)
    await db.delete(tag)
    await db.commit()
