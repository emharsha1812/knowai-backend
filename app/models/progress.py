from sqlalchemy import String, Boolean, Integer, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime
from app.core.database import Base
from app.models.base import TimestampMixin
import enum


class ContentType(str, enum.Enum):
    writing_post = "writing_post"
    lesson = "lesson"
    course = "course"
    problem = "problem"
    qna_lab = "qna_lab"
    concept = "concept"


class UserProgress(Base, TimestampMixin):
    """Tracks what a user has started or completed."""
    __tablename__ = "user_progress"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content_type: Mapped[ContentType] = mapped_column(
        SAEnum(ContentType, name="contenttype"),
        nullable=False,
    )
    content_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Progress percentage 0-100 (for courses)
    progress_pct: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user = relationship("User", back_populates="progress_records")
