from sqlalchemy import String, Text, Boolean, Integer, ForeignKey, Enum as SAEnum, Index
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.core.database import Base
from app.models.base import TimestampMixin
from app.models.content import DifficultyLevel


class Course(Base, TimestampMixin):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    subtitle: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        SAEnum(DifficultyLevel, name="difficultylevel", create_type=False),
        default=DifficultyLevel.intermediate,
        nullable=False,
    )
    cover_image_url: Mapped[str | None] = mapped_column(String(500))
    tags: Mapped[list | None] = mapped_column(JSONB, default=list)
    prerequisites: Mapped[list | None] = mapped_column(JSONB, default=list)
    estimated_hours: Mapped[int | None] = mapped_column(Integer)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Final project problem id
    final_project_problem_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("problems.id", ondelete="SET NULL"), nullable=True
    )
    search_vector: Mapped[str | None] = mapped_column(TSVECTOR)

    chapters = relationship(
        "Chapter", back_populates="course", order_by="Chapter.order", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_courses_search", "search_vector", postgresql_using="gin"),
    )


class Chapter(Base, TimestampMixin):
    __tablename__ = "chapters"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    course = relationship("Course", back_populates="chapters")
    lessons = relationship(
        "Lesson", back_populates="chapter", order_by="Lesson.order", cascade="all, delete-orphan"
    )


class Lesson(Base, TimestampMixin):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    chapter_id: Mapped[int] = mapped_column(
        ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)  # Markdown
    marimo_cells: Mapped[list | None] = mapped_column(JSONB, default=list)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reading_time_minutes: Mapped[int | None] = mapped_column(Integer)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Optional problem to cap the lesson
    problem_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("problems.id", ondelete="SET NULL"), nullable=True
    )
    search_vector: Mapped[str | None] = mapped_column(TSVECTOR)

    chapter = relationship("Chapter", back_populates="lessons")
    qna_lab = relationship("QnaLab", back_populates="lesson", uselist=False)

    __table_args__ = (
        Index("ix_lessons_search", "search_vector", postgresql_using="gin"),
    )
