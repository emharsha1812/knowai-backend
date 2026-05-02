from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.content import WritingPost
from app.models.user import User
from app.schemas.content import WritingPostCreate, WritingPostUpdate, WritingPostPublic, WritingPostSummary
from app.api.deps import get_current_admin, get_optional_user

router = APIRouter(prefix="/writing", tags=["writing"])


@router.get("", response_model=list[WritingPostSummary])
async def list_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tag: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    q = select(WritingPost).order_by(WritingPost.created_at.desc())
    # Non-admins only see published posts
    if not current_user or current_user.role.value != "admin":
        q = q.where(WritingPost.is_published == True)
    if tag:
        q = q.where(WritingPost.tags.contains([tag]))
    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{slug}", response_model=WritingPostPublic)
async def get_post(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    result = await db.execute(select(WritingPost).where(WritingPost.slug == slug))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not post.is_published and (not current_user or current_user.role.value != "admin"):
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("", response_model=WritingPostPublic, status_code=status.HTTP_201_CREATED)
async def create_post(
    body: WritingPostCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    existing = await db.execute(select(WritingPost).where(WritingPost.slug == body.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Slug already exists")

    post = WritingPost(
        **body.model_dump(exclude={"marimo_cells"}),
        marimo_cells=[c.model_dump() for c in body.marimo_cells],
    )
    db.add(post)
    await db.flush()
    await db.refresh(post)
    return post


@router.patch("/{slug}", response_model=WritingPostPublic)
async def update_post(
    slug: str,
    body: WritingPostUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(WritingPost).where(WritingPost.slug == slug))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = body.model_dump(exclude_unset=True)
    if "marimo_cells" in data and data["marimo_cells"] is not None:
        data["marimo_cells"] = [c.model_dump() for c in body.marimo_cells]
    for field, value in data.items():
        setattr(post, field, value)
    return post


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    slug: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(WritingPost).where(WritingPost.slug == slug))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    await db.delete(post)
