from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.qna import QnaLab, QnaQuestion, QnaResponse
from app.models.user import User
from app.schemas.qna import (
    QnaLabCreate, QnaLabUpdate, QnaLabPublic,
    QnaQuestionCreate, QnaQuestionUpdate, QnaQuestionPublic, QnaQuestionWithAnswer,
    QnaResponseCreate, QnaResponsePublic,
)
from app.api.deps import get_current_admin, get_current_user

router = APIRouter(prefix="/qna", tags=["qna"])


# ── Labs ──────────────────────────────────────────────────────────────────────

@router.get("/labs/{lab_id}", response_model=QnaLabPublic)
async def get_lab(lab_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(QnaLab)
        .where(QnaLab.id == lab_id, QnaLab.is_published == True)
        .options(selectinload(QnaLab.questions))
    )
    lab = result.scalar_one_or_none()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    return lab


@router.post("/labs", response_model=QnaLabPublic, status_code=status.HTTP_201_CREATED)
async def create_lab(
    body: QnaLabCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    if body.writing_post_id and body.lesson_id:
        raise HTTPException(status_code=400, detail="A lab can belong to either a post or a lesson, not both")

    lab = QnaLab(
        title=body.title,
        description=body.description,
        writing_post_id=body.writing_post_id,
        lesson_id=body.lesson_id,
        is_published=body.is_published,
    )
    db.add(lab)
    await db.flush()

    for q in body.questions:
        question = QnaQuestion(
            lab_id=lab.id,
            **q.model_dump(exclude={"options"}),
            options=[o.model_dump() for o in q.options] if q.options else None,
        )
        db.add(question)

    await db.flush()
    await db.refresh(lab)
    return lab


@router.patch("/labs/{lab_id}", response_model=QnaLabPublic)
async def update_lab(
    lab_id: int,
    body: QnaLabUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(QnaLab).where(QnaLab.id == lab_id))
    lab = result.scalar_one_or_none()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(lab, field, value)
    return lab


@router.delete("/labs/{lab_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lab(
    lab_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(QnaLab).where(QnaLab.id == lab_id))
    lab = result.scalar_one_or_none()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    await db.delete(lab)


# ── Questions ─────────────────────────────────────────────────────────────────

@router.post("/labs/{lab_id}/questions", response_model=QnaQuestionPublic, status_code=status.HTTP_201_CREATED)
async def add_question(
    lab_id: int,
    body: QnaQuestionCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(QnaLab).where(QnaLab.id == lab_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Lab not found")

    question = QnaQuestion(
        lab_id=lab_id,
        **body.model_dump(exclude={"options"}),
        options=[o.model_dump() for o in body.options] if body.options else None,
    )
    db.add(question)
    await db.flush()
    await db.refresh(question)
    return question


@router.patch("/questions/{question_id}", response_model=QnaQuestionPublic)
async def update_question(
    question_id: int,
    body: QnaQuestionUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(QnaQuestion).where(QnaQuestion.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    data = body.model_dump(exclude_unset=True)
    if "options" in data and data["options"] is not None:
        data["options"] = [o.model_dump() for o in body.options]
    for field, value in data.items():
        setattr(question, field, value)
    return question


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(QnaQuestion).where(QnaQuestion.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    await db.delete(question)


# ── Responses ─────────────────────────────────────────────────────────────────

@router.post("/questions/{question_id}/respond", response_model=QnaQuestionWithAnswer)
async def respond_to_question(
    question_id: int,
    body: QnaResponseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(QnaQuestion).where(QnaQuestion.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Upsert response
    existing = await db.execute(
        select(QnaResponse).where(
            QnaResponse.user_id == current_user.id,
            QnaResponse.question_id == question_id,
        )
    )
    response = existing.scalar_one_or_none()
    if response:
        response.response_text = body.response_text
        response.selected_option = body.selected_option
    else:
        response = QnaResponse(
            user_id=current_user.id,
            question_id=question_id,
            response_text=body.response_text,
            selected_option=body.selected_option,
        )
        db.add(response)

    # Return the question with the expected answer revealed
    return question
