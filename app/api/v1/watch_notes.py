from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.watch_note import WatchNote
from app.models.user import User
from app.schemas.watch_note import WatchNoteCreate, WatchNoteUpdate, WatchNotePublic, WatchNoteSummary
from app.api.deps import get_current_admin, get_optional_user

router = APIRouter(prefix="/watch-notes", tags=["watch-notes"])


@router.get("", response_model=list[WatchNoteSummary])
async def list_watch_notes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tag: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    q = select(WatchNote).order_by(WatchNote.created_at.desc())
    if not current_user or current_user.role.value != "admin":
        q = q.where(WatchNote.is_published == True)
    if tag:
        q = q.where(WatchNote.tag == tag)
    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{slug}", response_model=WatchNotePublic)
async def get_watch_note(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    result = await db.execute(select(WatchNote).where(WatchNote.slug == slug))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Watch note not found")
    if not note.is_published and (not current_user or current_user.role.value != "admin"):
        raise HTTPException(status_code=404, detail="Watch note not found")
    return note


@router.post("", response_model=WatchNotePublic, status_code=status.HTTP_201_CREATED)
async def create_watch_note(
    body: WatchNoteCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    existing = await db.execute(select(WatchNote).where(WatchNote.slug == body.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Slug already exists")
    note = WatchNote(
        **body.model_dump(exclude={"sections"}),
        sections=[s.model_dump() for s in body.sections],
    )
    db.add(note)
    await db.flush()
    await db.refresh(note)
    return note


@router.patch("/{slug}", response_model=WatchNotePublic)
async def update_watch_note(
    slug: str,
    body: WatchNoteUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(WatchNote).where(WatchNote.slug == slug))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Watch note not found")
    data = body.model_dump(exclude_unset=True)
    if "sections" in data and data["sections"] is not None:
        data["sections"] = [s.model_dump() for s in body.sections]
    for field, value in data.items():
        setattr(note, field, value)
    return note


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_watch_note(
    slug: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(WatchNote).where(WatchNote.slug == slug))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Watch note not found")
    await db.delete(note)
