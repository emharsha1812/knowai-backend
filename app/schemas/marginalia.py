from pydantic import BaseModel, field_validator
from datetime import datetime
from app.models.marginalia import NoteType


class MarginaliaNoteCreate(BaseModel):
    article_slug: str
    section_id: str | None = None
    note_type: NoteType = NoteType.note
    label: str | None = None
    content: str
    color: str | None = None

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()


class MarginaliaNoteUpdate(BaseModel):
    label: str | None = None
    content: str | None = None
    note_type: NoteType | None = None
    color: str | None = None

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip() if v else v


class MarginaliaNotePublic(BaseModel):
    id: int
    article_slug: str
    section_id: str | None
    note_type: NoteType
    label: str | None
    content: str
    color: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
