from pydantic import BaseModel
from datetime import datetime
from app.models.qna import QuestionType


# ── Questions ─────────────────────────────────────────────────────────────────

class QuestionOption(BaseModel):
    label: str
    is_correct: bool = False


class QnaQuestionCreate(BaseModel):
    question_type: QuestionType
    content: str
    expected_answer: str | None = None
    options: list[QuestionOption] | None = None
    order: int = 0


class QnaQuestionUpdate(BaseModel):
    question_type: QuestionType | None = None
    content: str | None = None
    expected_answer: str | None = None
    options: list[QuestionOption] | None = None
    order: int | None = None


class QnaQuestionPublic(BaseModel):
    id: int
    lab_id: int
    question_type: QuestionType
    content: str
    options: list | None
    order: int

    model_config = {"from_attributes": True}


class QnaQuestionWithAnswer(QnaQuestionPublic):
    """Returned after the user submits a response."""
    expected_answer: str | None


# ── Labs ──────────────────────────────────────────────────────────────────────

class QnaLabCreate(BaseModel):
    title: str
    description: str | None = None
    writing_post_id: int | None = None
    lesson_id: int | None = None
    is_published: bool = False
    questions: list[QnaQuestionCreate] = []


class QnaLabUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_published: bool | None = None


class QnaLabPublic(BaseModel):
    id: int
    title: str
    description: str | None
    writing_post_id: int | None
    lesson_id: int | None
    is_published: bool
    questions: list[QnaQuestionPublic] = []
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Responses ─────────────────────────────────────────────────────────────────

class QnaResponseCreate(BaseModel):
    response_text: str
    selected_option: int | None = None


class QnaResponsePublic(BaseModel):
    id: int
    user_id: int
    question_id: int
    response_text: str
    selected_option: int | None
    created_at: datetime

    model_config = {"from_attributes": True}
