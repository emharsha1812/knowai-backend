from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.search import SearchResponse
from app.services.search import full_text_search

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=2, max_length=200),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    return await full_text_search(
        db=db,
        query=q,
        limit=page_size,
        offset=(page - 1) * page_size,
    )
