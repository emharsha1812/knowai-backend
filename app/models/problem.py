from sqlalchemy import String, Text, Boolean, Integer, ForeignKey, Enum as SAEnum, Index
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.core.database import Base
from app.models.base import TimestampMixin
from app.models.content import DifficultyLevel
import enum


class ProblemCategory(str, enum.Enum):
    architecture = "architecture"
    training = "training"
    gpu_systems = "gpu_systems"
    paper_implementations = "paper_implementations"
    debugging = "debugging"
    math = "math"
    rl = "rl"
    data = "data"


class SubmissionStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    accepted = "accepted"
    wrong_answer = "wrong_answer"
    time_limit_exceeded = "time_limit_exceeded"
    memory_limit_exceeded = "memory_limit_exceeded"
    runtime_error = "runtime_error"
    compilation_error = "compilation_error"


class Problem(Base, TimestampMixin):
    __tablename__ = "problems"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)  # Markdown
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        SAEnum(DifficultyLevel, name="difficultylevel", create_type=False),
        default=DifficultyLevel.intermediate,
        nullable=False,
    )
    category: Mapped[ProblemCategory] = mapped_column(
        SAEnum(ProblemCategory, name="problemcategory"),
        nullable=False,
    )
    starter_code: Mapped[str] = mapped_column(Text, nullable=False)
    solution_code: Mapped[str] = mapped_column(Text, nullable=False)
    solution_explanation: Mapped[str | None] = mapped_column(Text)
    # [{input: ..., expected_output: ..., is_hidden: bool, description: str}]
    test_cases: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    hints: Mapped[list | None] = mapped_column(JSONB, default=list)
    tags: Mapped[list | None] = mapped_column(JSONB, default=list)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Link back to a writing post that explains the theory
    related_post_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("writing_posts.id", ondelete="SET NULL"), nullable=True
    )
    search_vector: Mapped[str | None] = mapped_column(TSVECTOR)

    submissions = relationship("ProblemSubmission", back_populates="problem", lazy="dynamic")

    __table_args__ = (
        Index("ix_problems_search", "search_vector", postgresql_using="gin"),
    )


class ProblemSubmission(Base, TimestampMixin):
    __tablename__ = "problem_submissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    problem_id: Mapped[int] = mapped_column(
        ForeignKey("problems.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(30), default="python", nullable=False)
    status: Mapped[SubmissionStatus] = mapped_column(
        SAEnum(SubmissionStatus, name="submissionstatus"),
        default=SubmissionStatus.pending,
        nullable=False,
    )
    # [{test_case_index, passed, actual_output, expected_output, error}]
    test_results: Mapped[list | None] = mapped_column(JSONB, default=list)
    execution_time_ms: Mapped[int | None] = mapped_column(Integer)
    memory_used_kb: Mapped[int | None] = mapped_column(Integer)

    user = relationship("User", back_populates="submissions")
    problem = relationship("Problem", back_populates="submissions")
