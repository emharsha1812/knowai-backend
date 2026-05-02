from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.core.database import get_db
from app.models.content import RoadmapItem
from app.models.user import User
from app.schemas.content import RoadmapItemCreate, RoadmapItemUpdate, RoadmapItemPublic
from app.api.deps import get_current_admin, get_current_user

router = APIRouter(prefix="/roadmap", tags=["roadmap"])


@router.get("", response_model=list[RoadmapItemPublic])
async def list_roadmap(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RoadmapItem).order_by(RoadmapItem.order))
    return result.scalars().all()


@router.post("", response_model=RoadmapItemPublic, status_code=status.HTTP_201_CREATED)
async def create_item(
    body: RoadmapItemCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    item = RoadmapItem(**body.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=RoadmapItemPublic)
async def update_item(
    item_id: int,
    body: RoadmapItemUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(RoadmapItem).where(RoadmapItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Roadmap item not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    return item


@router.post("/{item_id}/upvote", response_model=RoadmapItemPublic)
async def upvote_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(RoadmapItem).where(RoadmapItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Roadmap item not found")
    item.upvotes += 1
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(RoadmapItem).where(RoadmapItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Roadmap item not found")
    await db.delete(item)
