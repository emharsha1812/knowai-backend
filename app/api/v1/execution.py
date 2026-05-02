from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User
from app.schemas.execution import ExecuteRequest, ExecuteResponse
from app.services.execution import run_code
from app.api.deps import get_current_user

router = APIRouter(prefix="/execution", tags=["execution"])


@router.post("/run", response_model=ExecuteResponse)
async def execute_code(
    body: ExecuteRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Ad-hoc code execution endpoint — used for interactive Marimo cells
    and lesson sandbox runs. Only Python is supported.
    """
    if body.language != "python":
        raise HTTPException(status_code=400, detail="Only Python is supported")

    return await run_code(code=body.code, stdin=body.stdin)
