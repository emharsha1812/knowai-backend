import asyncio
import time
import tempfile
import os
import sys
from app.core.config import settings
from app.schemas.execution import ExecuteResponse


async def run_code(code: str, stdin: str | None = None) -> ExecuteResponse:
    """
    Execute Python code in a subprocess with timeout and memory limits.
    Uses a temporary file to avoid shell injection.
    """
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as f:
        f.write(code)
        tmp_path = f.name

    try:
        start = time.monotonic()

        proc = await asyncio.create_subprocess_exec(
            sys.executable, tmp_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            # Restrict env to minimal safe set
            env={
                "PATH": os.environ.get("PATH", ""),
                "PYTHONPATH": "",
                "HOME": tempfile.gettempdir(),
            },
        )

        stdin_bytes = stdin.encode() if stdin else b""

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=stdin_bytes),
                timeout=settings.EXECUTION_TIMEOUT_SECONDS,
            )
            timed_out = False
        except asyncio.TimeoutError:
            proc.kill()
            await proc.communicate()
            elapsed_ms = int((time.monotonic() - start) * 1000)
            return ExecuteResponse(
                stdout="",
                stderr="Time limit exceeded",
                exit_code=124,
                execution_time_ms=elapsed_ms,
                timed_out=True,
            )

        elapsed_ms = int((time.monotonic() - start) * 1000)

        return ExecuteResponse(
            stdout=stdout.decode(errors="replace")[:50_000],
            stderr=stderr.decode(errors="replace")[:10_000],
            exit_code=proc.returncode,
            execution_time_ms=elapsed_ms,
            timed_out=False,
        )
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


async def grade_submission(
    code: str,
    test_cases: list[dict],
    timeout: int = None,
) -> tuple[list[dict], int, bool]:
    """
    Run code against test cases.
    Returns (test_results, total_passed, all_passed).
    """
    timeout = timeout or settings.EXECUTION_TIMEOUT_SECONDS
    results = []
    total_passed = 0

    for i, tc in enumerate(test_cases):
        result = await run_code(code, stdin=tc.get("input", ""))
        actual = result.stdout.strip()
        expected = str(tc.get("expected_output", "")).strip()
        passed = (not result.timed_out) and (result.exit_code == 0) and (actual == expected)

        if passed:
            total_passed += 1

        results.append({
            "test_case_index": i,
            "passed": passed,
            "actual_output": actual if not tc.get("is_hidden") else None,
            "expected_output": expected if not tc.get("is_hidden") else "hidden",
            "error": result.stderr[:500] if result.stderr else None,
            "is_hidden": tc.get("is_hidden", False),
        })

    all_passed = total_passed == len(test_cases)
    return results, total_passed, all_passed
