import pytest
from app.services.execution import run_code, grade_submission


@pytest.mark.asyncio
async def test_run_hello_world():
    result = await run_code('print("hello world")')
    assert result.exit_code == 0
    assert "hello world" in result.stdout
    assert result.timed_out is False


@pytest.mark.asyncio
async def test_run_with_error():
    result = await run_code("raise ValueError('oops')")
    assert result.exit_code != 0
    assert "ValueError" in result.stderr


@pytest.mark.asyncio
async def test_run_with_stdin():
    result = await run_code("x = input()\nprint(int(x) * 2)", stdin="21")
    assert result.exit_code == 0
    assert "42" in result.stdout


@pytest.mark.asyncio
async def test_timeout():
    result = await run_code("import time\ntime.sleep(999)")
    assert result.timed_out is True


@pytest.mark.asyncio
async def test_grade_all_pass():
    code = "x = int(input())\nprint(x * 2)"
    test_cases = [
        {"input": "5", "expected_output": "10", "is_hidden": False},
        {"input": "0", "expected_output": "0", "is_hidden": False},
    ]
    results, total_passed, all_passed = await grade_submission(code, test_cases)
    assert all_passed is True
    assert total_passed == 2


@pytest.mark.asyncio
async def test_grade_partial_fail():
    code = "print('wrong')"
    test_cases = [
        {"input": "", "expected_output": "right", "is_hidden": False},
    ]
    results, total_passed, all_passed = await grade_submission(code, test_cases)
    assert all_passed is False
    assert total_passed == 0
