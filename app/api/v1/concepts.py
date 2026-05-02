from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.content import Concept
from app.models.user import User
from app.schemas.content import ConceptCreate, ConceptUpdate, ConceptPublic
from app.api.deps import get_current_admin, get_optional_user

router = APIRouter(prefix="/concepts", tags=["concepts"])


@router.get("", response_model=list[ConceptPublic])
async def list_concepts(
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=100),
    tag: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    q = select(Concept).order_by(Concept.title)
    if not current_user or current_user.role.value != "admin":
        q = q.where(Concept.is_published == True)
    if tag:
        q = q.where(Concept.tags.contains([tag]))
    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{slug}", response_model=ConceptPublic)
async def get_concept(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    result = await db.execute(select(Concept).where(Concept.slug == slug))
    concept = result.scalar_one_or_none()
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")
    if not concept.is_published and (not current_user or current_user.role.value != "admin"):
        raise HTTPException(status_code=404, detail="Concept not found")
    return concept


@router.post("", response_model=ConceptPublic, status_code=status.HTTP_201_CREATED)
async def create_concept(
    body: ConceptCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    existing = await db.execute(select(Concept).where(Concept.slug == body.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Slug already exists")
    concept = Concept(**body.model_dump())
    db.add(concept)
    await db.flush()
    await db.refresh(concept)
    return concept


@router.patch("/{slug}", response_model=ConceptPublic)
async def update_concept(
    slug: str,
    body: ConceptUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(Concept).where(Concept.slug == slug))
    concept = result.scalar_one_or_none()
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(concept, field, value)
    return concept


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_concept(
    slug: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(Concept).where(Concept.slug == slug))
    concept = result.scalar_one_or_none()
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")
    await db.delete(concept)
