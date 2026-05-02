import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_get_post(client: AsyncClient, admin_headers: dict):
    # Create
    resp = await client.post("/api/v1/writing", headers=admin_headers, json={
        "slug": "flash-attention",
        "title": "Flash Attention Explained",
        "content": "## Flash Attention\nHere is the explanation...",
        "tags": ["attention", "transformers"],
        "is_published": True,
    })
    assert resp.status_code == 201
    assert resp.json()["slug"] == "flash-attention"

    # Get
    resp = await client.get("/api/v1/writing/flash-attention")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Flash Attention Explained"


@pytest.mark.asyncio
async def test_unpublished_not_visible_to_public(client: AsyncClient, admin_headers: dict):
    await client.post("/api/v1/writing", headers=admin_headers, json={
        "slug": "draft-post",
        "title": "Draft",
        "content": "WIP",
        "is_published": False,
    })
    resp = await client.get("/api/v1/writing/draft-post")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_posts(client: AsyncClient, admin_headers: dict):
    await client.post("/api/v1/writing", headers=admin_headers, json={
        "slug": "list-test-post",
        "title": "List Test",
        "content": "Content here",
        "is_published": True,
    })
    resp = await client.get("/api/v1/writing")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_update_post(client: AsyncClient, admin_headers: dict):
    await client.post("/api/v1/writing", headers=admin_headers, json={
        "slug": "update-post",
        "title": "Original",
        "content": "Original content",
        "is_published": True,
    })
    resp = await client.patch("/api/v1/writing/update-post", headers=admin_headers, json={
        "title": "Updated Title",
    })
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_non_admin_cannot_create(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/writing", headers=auth_headers, json={
        "slug": "forbidden",
        "title": "Forbidden",
        "content": "No",
        "is_published": True,
    })
    assert resp.status_code == 403
