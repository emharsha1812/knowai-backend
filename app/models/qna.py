from sqlalchemy import String, Text, Integer, ForeignKey, Enum as SAEnum, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.core.database import Base
from app.models.base import TimestampMixin
import enum


class QuestionType(str, enum.Enum):
    conceptual = "conceptual"    # short answer, no autograding
    diagnostic = "diagnostic"   # pre-course knowledge check


class QnaLab(Base, TimestampMixin):
    """A set of questions attached to a Writing post or Lesson."""
    __tablename__ = "qna_labs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    # Exactly one of these is set
    writing_post_id: Mapped[int | None] = mapped_column(
        ForeignKey("writing_posts.id", ondelete="CASCADE"), nullable=True, index=True
    )
    lesson_id: Mapped[int | None] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"), nullable=True, index=True
    )
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    writing_post = relationship("WritingPost", back_populates="qna_lab")
    lesson = relationship("Lesson", back_populates="qna_lab")
    questions = relationship(
        "QnaQuestion", back_populates="lab", order_by="QnaQuestion.order", cascade="all, delete-orphan"
    )


class QnaQuestion(Base, TimestampMixin):
    __tablename__ = "qna_questions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    lab_id: Mapped[int] = mapped_column(
        ForeignKey("qna_labs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    question_type: Mapped[QuestionType] = mapped_column(
        SAEnum(QuestionType, name="questiontype"),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # For conceptual: a model answer the author writes; not shown until submitted
    expected_answer: Mapped[str | None] = mapped_column(Text)
    # For diagnostic: multiple choice options [{label, is_correct}]
    options: Mapped[list | None] = mapped_column(JSONB, default=None)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    lab = relationship("QnaLab", back_populates="questions")
    responses = relationship("QnaResponse", back_populates="question", lazy="dynamic")


class QnaResponse(Base, TimestampMixin):
    """A user's answer to a QnA question."""
    __tablename__ = "qna_responses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("qna_questions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    response_text: Mapped[str] = mapped_column(Text, nullable=False)
    # For diagnostic MCQ: selected option index
    selected_option: Mapped[int | None] = mapped_column(Integer)

    user = relationship("User", back_populates="qna_responses")
    question = relationship("QnaQuestion", back_populates="responses")
