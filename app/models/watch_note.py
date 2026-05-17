from sqlalchemy import String, Text, Boolean, Integer, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column, Mapped
from app.core.database import Base
from app.models.base import TimestampMixin


class WatchNote(Base, TimestampMixin):
    __tablename__ = "watch_notes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    youtube_video_id: Mapped[str] = mapped_column(String(50), nullable=False)
    channel: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str | None] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    duration: Mapped[str] = mapped_column(String(20), nullable=False)
    watched_ratio: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    note_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    page_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tag: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str] = mapped_column(String(50), default="lavender", nullable=False)
    last_note: Mapped[str | None] = mapped_column(Text)
    thumb_bg: Mapped[str] = mapped_column(String(20), default="#1a1a1a", nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Notes sections: [{ts, label, heading, body_md}]
    sections: Mapped[list | None] = mapped_column(JSONB, default=list)
    pdf_url: Mapped[str | None] = mapped_column(String(500))
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
