from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.problem import Problem, ProblemSubmission, SubmissionStatus
from app.models.user import User
from app.schemas.problem import (
    ProblemCreate, ProblemUpdate, ProblemPublic, ProblemWithSolution,
    ProblemSummary, SubmitCodeRequest, SubmissionPublic,
)
from app.api.deps import get_current_admin, get_current_user, get_optional_user
from app.services.execution import grade_submission

router = APIRouter(prefix="/problems", tags=["problems"])


@router.get("", response_model=list[ProblemSummary])
async def list_problems(
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=100),
    difficulty: str | None = Query(None),
    category: str | None = Query(None),
    tag: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    q = select(Problem).order_by(Problem.created_at.desc())
    if not current_user or current_user.role.value != "admin":
        q = q.where(Problem.is_published == True)
    if difficulty:
        q = q.where(Problem.difficulty == difficulty)
    if category:
        q = q.where(Problem.category == category)
    if tag:
        q = q.where(Problem.tags.contains([tag]))
    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{slug}", response_model=ProblemPublic)
async def get_problem(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    result = await db.execute(select(Problem).where(Problem.slug == slug))
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    if not problem.is_published and (not current_user or current_user.role.value != "admin"):
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


@router.get("/{slug}/solution", response_model=ProblemWithSolution)
async def get_solution(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns the solution only if the user has an accepted submission for this problem.
    """
    result = await db.execute(select(Problem).where(Problem.slug == slug))
    problem = result.scalar_one_or_none()
    if not problem or not problem.is_published:
        raise HTTPException(status_code=404, detail="Problem not found")

    # Admins can always see solutions
    if current_user.role.value != "admin":
        accepted = await db.execute(
            select(ProblemSubmission).where(
                ProblemSubmission.user_id == current_user.id,
                ProblemSubmission.problem_id == problem.id,
                ProblemSubmission.status == SubmissionStatus.accepted,
            )
        )
        if not accepted.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Solve the problem first to unlock the solution")

    return problem


@router.post("", response_model=ProblemPublic, status_code=status.HTTP_201_CREATED)
async def create_problem(
    body: ProblemCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    existing = await db.execute(select(Problem).where(Problem.slug == body.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Slug already exists")

    problem = Problem(
        **body.model_dump(exclude={"test_cases", "hints"}),
        test_cases=[tc.model_dump() for tc in body.test_cases],
        hints=body.hints,
    )
    db.add(problem)
    await db.flush()
    await db.refresh(problem)
    return problem


@router.patch("/{slug}", response_model=ProblemPublic)
async def update_problem(
    slug: str,
    body: ProblemUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(Problem).where(Problem.slug == slug))
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    data = body.model_dump(exclude_unset=True)
    if "test_cases" in data and data["test_cases"] is not None:
        data["test_cases"] = [tc.model_dump() for tc in body.test_cases]
    for field, value in data.items():
        setattr(problem, field, value)
    return problem


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_problem(
    slug: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(Problem).where(Problem.slug == slug))
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    await db.delete(problem)


# ── Submissions ───────────────────────────────────────────────────────────────

@router.post("/{slug}/submit", response_model=SubmissionPublic)
async def submit_solution(
    slug: str,
    body: SubmitCodeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Problem).where(Problem.slug == slug, Problem.is_published == True))
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    submission = ProblemSubmission(
        user_id=current_user.id,
        problem_id=problem.id,
        code=body.code,
        language=body.language,
        status=SubmissionStatus.running,
    )
    db.add(submission)
    await db.flush()

    # Grade against test cases
    test_results, total_passed, all_passed = await grade_submission(
        code=body.code,
        test_cases=problem.test_cases,
    )

    # Determine status from results
    if all_passed:
        final_status = SubmissionStatus.accepted
    else:
        # Check if any timed out
        timed_out_any = any(r.get("error", "").startswith("Time") for r in test_results if r.get("error"))
        final_status = SubmissionStatus.time_limit_exceeded if timed_out_any else SubmissionStatus.wrong_answer

    execution_time = max((r.get("execution_time_ms", 0) or 0) for r in test_results) if test_results else None

    submission.status = final_status
    submission.test_results = test_results

    return submission


@router.get("/{slug}/submissions", response_model=list[SubmissionPublic])
async def my_submissions(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Problem).where(Problem.slug == slug))
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    subs = await db.execute(
        select(ProblemSubmission)
        .where(
            ProblemSubmission.user_id == current_user.id,
            ProblemSubmission.problem_id == problem.id,
        )
        .order_by(ProblemSubmission.created_at.desc())
        .limit(20)
    )
    return subs.scalars().all()
