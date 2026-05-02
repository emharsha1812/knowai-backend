from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.course import Course, Chapter, Lesson
from app.models.user import User
from app.schemas.course import (
    CourseCreate, CourseUpdate, CoursePublic, CourseSummary,
    ChapterCreate, ChapterUpdate, ChapterPublic,
    LessonCreate, LessonUpdate, LessonPublic,
)
from app.api.deps import get_current_admin, get_optional_user
from app.services.course_catalog import CATALOG_BY_SLUG, LESSON_BY_SLUG, catalog_course_summaries

router = APIRouter(prefix="/courses", tags=["courses"])


def _course_payload(course: Course, chapters: list | None = None) -> dict:
    return {
        "id": course.id,
        "slug": course.slug,
        "title": course.title,
        "subtitle": course.subtitle,
        "description": course.description,
        "difficulty": course.difficulty,
        "cover_image_url": course.cover_image_url,
        "tags": course.tags,
        "prerequisites": course.prerequisites,
        "estimated_hours": course.estimated_hours,
        "is_published": course.is_published,
        "final_project_problem_id": course.final_project_problem_id,
        "chapters": chapters if chapters is not None else [],
        "created_at": course.created_at,
        "updated_at": course.updated_at,
    }


def _chapter_payload(chapter: Chapter, lessons: list | None = None) -> dict:
    return {
        "id": chapter.id,
        "course_id": chapter.course_id,
        "title": chapter.title,
        "description": chapter.description,
        "order": chapter.order,
        "lessons": lessons if lessons is not None else [],
        "created_at": chapter.created_at,
    }


# ── Courses ───────────────────────────────────────────────────────────────────

@router.get("", response_model=list[CourseSummary])
async def list_courses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    difficulty: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    q = select(Course).order_by(Course.created_at.desc())
    if not current_user or current_user.role.value != "admin":
        q = q.where(Course.is_published == True)
    if difficulty:
        q = q.where(Course.difficulty == difficulty)
    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    courses = list(result.scalars().all())

    if page == 1 and len(courses) < page_size:
        existing_slugs = {course.slug for course in courses}
        courses.extend(
            catalog_course_summaries(
                difficulty=difficulty,
                exclude_slugs=existing_slugs,
            )[: page_size - len(courses)]
        )

    return courses


@router.get("/{slug}", response_model=CoursePublic)
async def get_course(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    result = await db.execute(
        select(Course)
        .where(Course.slug == slug)
        .options(
            selectinload(Course.chapters).selectinload(Chapter.lessons)
        )
    )
    course = result.scalar_one_or_none()
    if not course:
        catalog_course = CATALOG_BY_SLUG.get(slug)
        if catalog_course:
            return catalog_course
        raise HTTPException(status_code=404, detail="Course not found")
    if not course.is_published and (not current_user or current_user.role.value != "admin"):
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("", response_model=CoursePublic, status_code=status.HTTP_201_CREATED)
async def create_course(
    body: CourseCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    existing = await db.execute(select(Course).where(Course.slug == body.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Slug already exists")
    course = Course(**body.model_dump())
    db.add(course)
    await db.flush()
    await db.refresh(course)
    return _course_payload(course)


@router.patch("/{slug}", response_model=CoursePublic)
async def update_course(
    slug: str,
    body: CourseUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(Course).where(Course.slug == slug))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(course, field, value)
    await db.flush()
    await db.refresh(course)
    return _course_payload(course)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    slug: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(Course).where(Course.slug == slug))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    await db.delete(course)


# ── Chapters ──────────────────────────────────────────────────────────────────

@router.post("/{slug}/chapters", response_model=ChapterPublic, status_code=status.HTTP_201_CREATED)
async def create_chapter(
    slug: str,
    body: ChapterCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(Course).where(Course.slug == slug))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    chapter = Chapter(course_id=course.id, **body.model_dump())
    db.add(chapter)
    await db.flush()
    await db.refresh(chapter)
    return _chapter_payload(chapter)


@router.patch("/chapters/{chapter_id}", response_model=ChapterPublic)
async def update_chapter(
    chapter_id: int,
    body: ChapterUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(chapter, field, value)
    await db.flush()
    await db.refresh(chapter)
    return _chapter_payload(chapter)


@router.delete("/chapters/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chapter(
    chapter_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    await db.delete(chapter)


# ── Lessons ───────────────────────────────────────────────────────────────────

@router.post("/chapters/{chapter_id}/lessons", response_model=LessonPublic, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    chapter_id: int,
    body: LessonCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Chapter not found")

    existing = await db.execute(select(Lesson).where(Lesson.slug == body.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Slug already exists")

    lesson = Lesson(
        chapter_id=chapter_id,
        **body.model_dump(exclude={"marimo_cells"}),
        marimo_cells=[c.model_dump() for c in body.marimo_cells],
    )
    db.add(lesson)
    await db.flush()
    await db.refresh(lesson)
    return lesson


@router.get("/lessons/{slug}", response_model=LessonPublic)
async def get_lesson(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    result = await db.execute(select(Lesson).where(Lesson.slug == slug))
    lesson = result.scalar_one_or_none()
    if not lesson:
        catalog_lesson = LESSON_BY_SLUG.get(slug)
        if catalog_lesson:
            return catalog_lesson
        raise HTTPException(status_code=404, detail="Lesson not found")
    if not lesson.is_published and (not current_user or current_user.role.value != "admin"):
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


@router.patch("/lessons/{lesson_id}", response_model=LessonPublic)
async def update_lesson(
    lesson_id: int,
    body: LessonUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    data = body.model_dump(exclude_unset=True)
    if "marimo_cells" in data and data["marimo_cells"] is not None:
        data["marimo_cells"] = [c.model_dump() for c in body.marimo_cells]
    for field, value in data.items():
        setattr(lesson, field, value)
    return lesson


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    await db.delete(lesson)
