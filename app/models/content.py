from sqlalchemy import String, Text, Boolean, Integer, Enum as SAEnum, Index
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.core.database import Base
from app.models.base import TimestampMixin
import enum


class DifficultyLevel(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class RoadmapStatus(str, enum.Enum):
    writing = "writing"
    planned = "planned"
    suggested = "suggested"
    published = "published"


class WritingPost(Base, TimestampMixin):
    __tablename__ = "writing_posts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    subtitle: Mapped[str | None] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text, nullable=False)  # Markdown
    # Marimo cells stored as [{id, code, type}]
    marimo_cells: Mapped[list | None] = mapped_column(JSONB, default=list)
    tags: Mapped[list | None] = mapped_column(JSONB, default=list)
    cover_image_url: Mapped[str | None] = mapped_column(String(500))
    reading_time_minutes: Mapped[int | None] = mapped_column(Integer)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Full-text search vector (populated by trigger or on write)
    search_vector: Mapped[str | None] = mapped_column(TSVECTOR)

    qna_lab = relationship("QnaLab", back_populates="writing_post", uselist=False)

    __table_args__ = (
        Index("ix_writing_posts_search", "search_vector", postgresql_using="gin"),
    )


class Concept(Base, TimestampMixin):
    __tablename__ = "concepts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    # 300-800 words explanation
    body: Mapped[str] = mapped_column(Text, nullable=False)
    example_code: Mapped[str | None] = mapped_column(Text)
    # Foreign key references stored as arrays of IDs
    related_post_ids: Mapped[list | None] = mapped_column(JSONB, default=list)
    related_problem_ids: Mapped[list | None] = mapped_column(JSONB, default=list)
    related_course_ids: Mapped[list | None] = mapped_column(JSONB, default=list)
    tags: Mapped[list | None] = mapped_column(JSONB, default=list)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    search_vector: Mapped[str | None] = mapped_column(TSVECTOR)

    __table_args__ = (
        Index("ix_concepts_search", "search_vector", postgresql_using="gin"),
    )


class RoadmapItem(Base, TimestampMixin):
    __tablename__ = "roadmap_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[RoadmapStatus] = mapped_column(
        SAEnum(RoadmapStatus, name="roadmapstatus"),
        default=RoadmapStatus.planned,
        nullable=False,
    )
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    upvotes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
