import pytest
from httpx import AsyncClient

_PROBLEM_PAYLOAD = {
    "slug": "softmax-impl",
    "title": "Implement Softmax",
    "description": "Implement the softmax function from scratch.",
    "difficulty": "intermediate",
    "category": "architecture",
    "starter_code": "import numpy as np\n\ndef softmax(x):\n    pass",
    "solution_code": "import numpy as np\n\ndef softmax(x):\n    e = np.exp(x - np.max(x))\n    return e / e.sum()",
    "test_cases": [
        {"input": "import numpy as np\nprint(softmax(np.array([1.0, 2.0, 3.0])))", "expected_output": "[0.09003057 0.24472847 0.66524096]", "is_hidden": False},
    ],
    "is_published": True,
}


@pytest.mark.asyncio
async def test_create_problem(client: AsyncClient, admin_headers: dict):
    resp = await client.post("/api/v1/problems", headers=admin_headers, json=_PROBLEM_PAYLOAD)
    assert resp.status_code == 201
    assert resp.json()["slug"] == "softmax-impl"


@pytest.mark.asyncio
async def test_list_problems(client: AsyncClient, admin_headers: dict):
    await client.post("/api/v1/problems", headers=admin_headers, json={**_PROBLEM_PAYLOAD, "slug": "list-p"})
    resp = await client.get("/api/v1/problems")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_get_problem(client: AsyncClient, admin_headers: dict):
    await client.post("/api/v1/problems", headers=admin_headers, json={**_PROBLEM_PAYLOAD, "slug": "get-p"})
    resp = await client.get("/api/v1/problems/get-p")
    assert resp.status_code == 200
    assert "starter_code" in resp.json()
    assert "solution_code" not in resp.json()


@pytest.mark.asyncio
async def test_solution_locked_before_solving(client: AsyncClient, admin_headers: dict, auth_headers: dict):
    await client.post("/api/v1/problems", headers=admin_headers, json={**_PROBLEM_PAYLOAD, "slug": "locked-p"})
    resp = await client.get("/api/v1/problems/locked-p/solution", headers=auth_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
