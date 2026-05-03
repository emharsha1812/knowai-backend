from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.marginalia import Marginalia
from app.models.user import User
from app.schemas.marginalia import MarginaliaNoteCreate, MarginaliaNoteUpdate, MarginaliaNotePublic
from app.api.deps import get_current_user

router = APIRouter(prefix="/marginalia", tags=["marginalia"])


@router.get("/{article_slug}", response_model=list[MarginaliaNotePublic])
async def get_notes(
    article_slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Marginalia)
        .where(Marginalia.user_id == current_user.id)
        .where(Marginalia.article_slug == article_slug)
        .order_by(Marginalia.created_at.asc())
    )
    return result.scalars().all()


@router.post("", response_model=MarginaliaNotePublic, status_code=status.HTTP_201_CREATED)
async def create_note(
    body: MarginaliaNoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = Marginalia(**body.model_dump(), user_id=current_user.id)
    db.add(note)
    await db.flush()
    await db.refresh(note)
    return note


@router.patch("/{note_id}", response_model=MarginaliaNotePublic)
async def update_note(
    note_id: int,
    body: MarginaliaNoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Marginalia)
        .where(Marginalia.id == note_id)
        .where(Marginalia.user_id == current_user.id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    for field, val in body.model_dump(exclude_unset=True).items():
        setattr(note, field, val)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Marginalia)
        .where(Marginalia.id == note_id)
        .where(Marginalia.user_id == current_user.id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    await db.delete(note)
