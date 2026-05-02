from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.playlist import Playlist, PlaylistItem
from app.models.user import User
from app.schemas.playlist import PlaylistCreate, PlaylistUpdate, PlaylistPublic, PlaylistItemCreate, PlaylistItemPublic
from app.api.deps import get_current_admin

router = APIRouter(prefix="/playlists", tags=["playlists"])


@router.get("", response_model=list[PlaylistPublic])
async def list_playlists(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Playlist)
        .where(Playlist.is_published == True)
        .options(selectinload(Playlist.items))
        .order_by(Playlist.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{slug}", response_model=PlaylistPublic)
async def get_playlist(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Playlist)
        .where(Playlist.slug == slug, Playlist.is_published == True)
        .options(selectinload(Playlist.items))
    )
    playlist = result.scalar_one_or_none()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return playlist


@router.post("", response_model=PlaylistPublic, status_code=status.HTTP_201_CREATED)
async def create_playlist(
    body: PlaylistCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    existing = await db.execute(select(Playlist).where(Playlist.slug == body.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Slug already exists")

    playlist = Playlist(
        slug=body.slug,
        title=body.title,
        description=body.description,
        playlist_type=body.playlist_type,
        is_published=body.is_published,
    )
    db.add(playlist)
    await db.flush()

    for item in body.items:
        db.add(PlaylistItem(playlist_id=playlist.id, **item.model_dump()))

    await db.flush()
    await db.refresh(playlist)
    return playlist


@router.patch("/{slug}", response_model=PlaylistPublic)
async def update_playlist(
    slug: str,
    body: PlaylistUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(Playlist).where(Playlist.slug == slug))
    playlist = result.scalar_one_or_none()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(playlist, field, value)
    return playlist


@router.post("/{slug}/items", response_model=PlaylistItemPublic, status_code=status.HTTP_201_CREATED)
async def add_item(
    slug: str,
    body: PlaylistItemCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(Playlist).where(Playlist.slug == slug))
    playlist = result.scalar_one_or_none()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    item = PlaylistItem(playlist_id=playlist.id, **body.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_playlist(
    slug: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(Playlist).where(Playlist.slug == slug))
    playlist = result.scalar_one_or_none()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    await db.delete(playlist)
