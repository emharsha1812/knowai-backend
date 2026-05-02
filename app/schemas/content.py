from pydantic import BaseModel
from datetime import datetime
from app.models.content import RoadmapStatus


# ── Writing Posts ─────────────────────────────────────────────────────────────

class MarimoCell(BaseModel):
    id: str
    code: str
    cell_type: str = "code"  # code | markdown


class WritingPostCreate(BaseModel):
    slug: str
    title: str
    subtitle: str | None = None
    content: str
    marimo_cells: list[MarimoCell] = []
    tags: list[str] = []
    cover_image_url: str | None = None
    reading_time_minutes: int | None = None
    is_published: bool = False


class WritingPostUpdate(BaseModel):
    title: str | None = None
    subtitle: str | None = None
    content: str | None = None
    marimo_cells: list[MarimoCell] | None = None
    tags: list[str] | None = None
    cover_image_url: str | None = None
    reading_time_minutes: int | None = None
    is_published: bool | None = None


class WritingPostPublic(BaseModel):
    id: int
    slug: str
    title: str
    subtitle: str | None
    content: str
    marimo_cells: list | None
    tags: list | None
    cover_image_url: str | None
    reading_time_minutes: int | None
    is_published: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WritingPostSummary(BaseModel):
    id: int
    slug: str
    title: str
    subtitle: str | None
    tags: list | None
    reading_time_minutes: int | None
    is_published: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Concepts ──────────────────────────────────────────────────────────────────

class ConceptCreate(BaseModel):
    slug: str
    title: str
    body: str
    example_code: str | None = None
    related_post_ids: list[int] = []
    related_problem_ids: list[int] = []
    related_course_ids: list[int] = []
    tags: list[str] = []
    is_published: bool = False


class ConceptUpdate(BaseModel):
    title: str | None = None
    body: str | None = None
    example_code: str | None = None
    related_post_ids: list[int] | None = None
    related_problem_ids: list[int] | None = None
    related_course_ids: list[int] | None = None
    tags: list[str] | None = None
    is_published: bool | None = None


class ConceptPublic(BaseModel):
    id: int
    slug: str
    title: str
    body: str
    example_code: str | None
    related_post_ids: list | None
    related_problem_ids: list | None
    related_course_ids: list | None
    tags: list | None
    is_published: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Roadmap ───────────────────────────────────────────────────────────────────

class RoadmapItemCreate(BaseModel):
    title: str
    description: str | None = None
    status: RoadmapStatus = RoadmapStatus.planned
    order: int = 0


class RoadmapItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: RoadmapStatus | None = None
    order: int | None = None


class RoadmapItemPublic(BaseModel):
    id: int
    title: str
    description: str | None
    status: RoadmapStatus
    order: int
    upvotes: int
    created_at: datetime

    model_config = {"from_attributes": True}
