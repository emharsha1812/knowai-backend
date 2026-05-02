from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timezone
from app.core.database import get_db
from app.models.progress import UserProgress, ContentType
from app.models.course import Course, Chapter, Lesson
from app.models.user import User
from app.schemas.progress import ProgressUpsert, ProgressPublic, CourseDashboard
from app.api.deps import get_current_user

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("", response_model=list[ProgressPublic])
async def my_progress(
    content_type: ContentType | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(UserProgress).where(UserProgress.user_id == current_user.id)
    if content_type:
        q = q.where(UserProgress.content_type == content_type)
    q = q.order_by(UserProgress.updated_at.desc())
    result = await db.execute(q)
    return result.scalars().all()


@router.post("", response_model=ProgressPublic)
async def upsert_progress(
    body: ProgressUpsert,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = await db.execute(
        select(UserProgress).where(
            UserProgress.user_id == current_user.id,
            UserProgress.content_type == body.content_type,
            UserProgress.content_id == body.content_id,
        )
    )
    record = existing.scalar_one_or_none()

    now = datetime.now(timezone.utc)
    if record:
        record.is_completed = body.is_completed
        record.progress_pct = body.progress_pct
        if body.is_completed and not record.completed_at:
            record.completed_at = now
    else:
        record = UserProgress(
            user_id=current_user.id,
            content_type=body.content_type,
            content_id=body.content_id,
            is_completed=body.is_completed,
            progress_pct=body.progress_pct,
            completed_at=now if body.is_completed else None,
        )
        db.add(record)

    await db.flush()
    await db.refresh(record)
    return record


@router.get("/courses/{course_id}", response_model=CourseDashboard)
async def course_progress(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Count total lessons in the course
    total_q = (
        select(func.count(Lesson.id))
        .join(Chapter, Lesson.chapter_id == Chapter.id)
        .where(Chapter.course_id == course_id, Lesson.is_published == True)
    )
    total_result = await db.execute(total_q)
    total_lessons = total_result.scalar() or 0

    # Count completed lessons
    completed_q = (
        select(func.count(UserProgress.id))
        .join(Lesson, UserProgress.content_id == Lesson.id)
        .join(Chapter, Lesson.chapter_id == Chapter.id)
        .where(
            UserProgress.user_id == current_user.id,
            UserProgress.content_type == ContentType.lesson,
            UserProgress.is_completed == True,
            Chapter.course_id == course_id,
        )
    )
    completed_result = await db.execute(completed_q)
    completed_lessons = completed_result.scalar() or 0

    pct = int((completed_lessons / total_lessons) * 100) if total_lessons else 0
    is_completed = pct == 100

    return CourseDashboard(
        course_id=course_id,
        total_lessons=total_lessons,
        completed_lessons=completed_lessons,
        progress_pct=pct,
        is_completed=is_completed,
    )
