from pydantic import BaseModel
from datetime import datetime


class WatchNoteSectionSchema(BaseModel):
    ts: str
    label: str
    heading: str
    body_md: str = ""


class WatchNoteCreate(BaseModel):
    slug: str
    youtube_video_id: str
    channel: str
    author: str | None = None
    title: str
    duration: str
    watched_ratio: float = 0.0
    note_count: int = 0
    page_count: int = 0
    tag: str
    color: str = "lavender"
    last_note: str | None = None
    thumb_bg: str = "#1a1a1a"
    is_published: bool = False
    is_featured: bool = False
    sections: list[WatchNoteSectionSchema] = []
    pdf_url: str | None = None


class WatchNoteUpdate(BaseModel):
    channel: str | None = None
    author: str | None = None
    title: str | None = None
    duration: str | None = None
    watched_ratio: float | None = None
    note_count: int | None = None
    page_count: int | None = None
    tag: str | None = None
    color: str | None = None
    last_note: str | None = None
    thumb_bg: str | None = None
    is_published: bool | None = None
    is_featured: bool | None = None
    sections: list[WatchNoteSectionSchema] | None = None
    pdf_url: str | None = None


class WatchNoteSummary(BaseModel):
    id: int
    slug: str
    youtube_video_id: str
    channel: str
    author: str | None
    title: str
    duration: str
    watched_ratio: float
    note_count: int
    page_count: int
    tag: str
    color: str
    last_note: str | None
    thumb_bg: str
    is_featured: bool
    is_published: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class WatchNotePublic(WatchNoteSummary):
    sections: list | None
    pdf_url: str | None
    view_count: int
    updated_at: datetime

    model_config = {"from_attributes": True}
