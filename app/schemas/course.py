from pydantic import BaseModel
from datetime import datetime
from app.models.content import DifficultyLevel
from app.schemas.content import MarimoCell


# ── Lesson ────────────────────────────────────────────────────────────────────

class LessonCreate(BaseModel):
    slug: str
    title: str
    content: str
    marimo_cells: list[MarimoCell] = []
    order: int = 0
    reading_time_minutes: int | None = None
    is_published: bool = False
    problem_id: int | None = None


class LessonUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    marimo_cells: list[MarimoCell] | None = None
    order: int | None = None
    reading_time_minutes: int | None = None
    is_published: bool | None = None
    problem_id: int | None = None


class LessonPublic(BaseModel):
    id: int
    chapter_id: int
    slug: str
    title: str
    content: str
    marimo_cells: list | None
    order: int
    reading_time_minutes: int | None
    is_published: bool
    problem_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LessonSummary(BaseModel):
    id: int
    slug: str
    title: str
    order: int
    reading_time_minutes: int | None
    is_published: bool
    problem_id: int | None

    model_config = {"from_attributes": True}


# ── Chapter ───────────────────────────────────────────────────────────────────

class ChapterCreate(BaseModel):
    title: str
    description: str | None = None
    order: int = 0


class ChapterUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    order: int | None = None


class ChapterPublic(BaseModel):
    id: int
    course_id: int
    title: str
    description: str | None
    order: int
    lessons: list[LessonSummary] = []
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Course ────────────────────────────────────────────────────────────────────

class CourseCreate(BaseModel):
    slug: str
    title: str
    subtitle: str | None = None
    description: str
    difficulty: DifficultyLevel = DifficultyLevel.intermediate
    cover_image_url: str | None = None
    tags: list[str] = []
    prerequisites: list[str] = []
    estimated_hours: int | None = None
    is_published: bool = False
    final_project_problem_id: int | None = None


class CourseUpdate(BaseModel):
    title: str | None = None
    subtitle: str | None = None
    description: str | None = None
    difficulty: DifficultyLevel | None = None
    cover_image_url: str | None = None
    tags: list[str] | None = None
    prerequisites: list[str] | None = None
    estimated_hours: int | None = None
    is_published: bool | None = None
    final_project_problem_id: int | None = None


class CoursePublic(BaseModel):
    id: int
    slug: str
    title: str
    subtitle: str | None
    description: str
    difficulty: DifficultyLevel
    cover_image_url: str | None
    tags: list | None
    prerequisites: list | None
    estimated_hours: int | None
    is_published: bool
    final_project_problem_id: int | None
    chapters: list[ChapterPublic] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CourseSummary(BaseModel):
    id: int
    slug: str
    title: str
    subtitle: str | None
    difficulty: DifficultyLevel
    tags: list | None
    estimated_hours: int | None
    is_published: bool
    created_at: datetime

    model_config = {"from_attributes": True}
