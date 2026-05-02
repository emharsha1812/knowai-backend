from pydantic import BaseModel


class ExecuteRequest(BaseModel):
    code: str
    language: str = "python"
    # Optional stdin for the program
    stdin: str | None = None


class ExecuteResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: int
    timed_out: bool = False
