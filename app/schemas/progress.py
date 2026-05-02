from pydantic import BaseModel
from datetime import datetime
from app.models.progress import ContentType


class ProgressUpsert(BaseModel):
    content_type: ContentType
    content_id: int
    is_completed: bool = False
    progress_pct: int = 0


class ProgressPublic(BaseModel):
    id: int
    user_id: int
    content_type: ContentType
    content_id: int
    is_completed: bool
    completed_at: datetime | None
    progress_pct: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CourseDashboard(BaseModel):
    course_id: int
    total_lessons: int
    completed_lessons: int
    progress_pct: int
    is_completed: bool
