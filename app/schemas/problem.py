from pydantic import BaseModel
from datetime import datetime
from app.models.content import DifficultyLevel
from app.models.problem import ProblemCategory, SubmissionStatus


# ── Test Case ─────────────────────────────────────────────────────────────────

class TestCase(BaseModel):
    input: str
    expected_output: str
    is_hidden: bool = False
    description: str | None = None


# ── Problem ───────────────────────────────────────────────────────────────────

class ProblemCreate(BaseModel):
    slug: str
    title: str
    description: str
    difficulty: DifficultyLevel = DifficultyLevel.intermediate
    category: ProblemCategory
    starter_code: str
    solution_code: str
    solution_explanation: str | None = None
    test_cases: list[TestCase] = []
    hints: list[str] = []
    tags: list[str] = []
    is_published: bool = False
    related_post_id: int | None = None


class ProblemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    difficulty: DifficultyLevel | None = None
    category: ProblemCategory | None = None
    starter_code: str | None = None
    solution_code: str | None = None
    solution_explanation: str | None = None
    test_cases: list[TestCase] | None = None
    hints: list[str] | None = None
    tags: list[str] | None = None
    is_published: bool | None = None
    related_post_id: int | None = None


class ProblemPublic(BaseModel):
    id: int
    slug: str
    title: str
    description: str
    difficulty: DifficultyLevel
    category: ProblemCategory
    starter_code: str
    hints: list | None
    tags: list | None
    is_published: bool
    related_post_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProblemWithSolution(ProblemPublic):
    """Returned only after the user has solved the problem."""
    solution_code: str
    solution_explanation: str | None
    test_cases: list  # includes hidden ones


class ProblemSummary(BaseModel):
    id: int
    slug: str
    title: str
    difficulty: DifficultyLevel
    category: ProblemCategory
    tags: list | None
    is_published: bool

    model_config = {"from_attributes": True}


# ── Submission ────────────────────────────────────────────────────────────────

class SubmitCodeRequest(BaseModel):
    code: str
    language: str = "python"


class TestResult(BaseModel):
    test_case_index: int
    passed: bool
    actual_output: str | None
    expected_output: str
    error: str | None = None
    is_hidden: bool = False


class SubmissionPublic(BaseModel):
    id: int
    user_id: int
    problem_id: int
    code: str
    language: str
    status: SubmissionStatus
    test_results: list | None
    execution_time_ms: int | None
    memory_used_kb: int | None
    created_at: datetime

    model_config = {"from_attributes": True}
