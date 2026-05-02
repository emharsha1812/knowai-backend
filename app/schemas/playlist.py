from pydantic import BaseModel
from datetime import datetime
from app.models.playlist import PlaylistType


class PlaylistItemCreate(BaseModel):
    order: int = 0
    problem_id: int | None = None
    question_id: int | None = None
    note: str | None = None


class PlaylistItemPublic(BaseModel):
    id: int
    order: int
    problem_id: int | None
    question_id: int | None
    note: str | None

    model_config = {"from_attributes": True}


class PlaylistCreate(BaseModel):
    slug: str
    title: str
    description: str | None = None
    playlist_type: PlaylistType
    is_published: bool = False
    items: list[PlaylistItemCreate] = []


class PlaylistUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_published: bool | None = None


class PlaylistPublic(BaseModel):
    id: int
    slug: str
    title: str
    description: str | None
    playlist_type: PlaylistType
    is_published: bool
    items: list[PlaylistItemPublic] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
