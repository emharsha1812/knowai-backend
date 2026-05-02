import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    resp = await client.post("/api/v1/auth/register", json={
        "email": "new@knowai.dev",
        "username": "newuser",
        "password": "password123",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient):
    payload = {"email": "dup@knowai.dev", "username": "dupuser", "password": "pass"}
    await client.post("/api/v1/auth/register", json=payload)
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "email": "login@knowai.dev",
        "username": "loginuser",
        "password": "mypassword",
    })
    resp = await client.post("/api/v1/auth/login", json={
        "email": "login@knowai.dev",
        "password": "mypassword",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "email": "wrong@knowai.dev",
        "username": "wronguser",
        "password": "correct",
    })
    resp = await client.post("/api/v1/auth/login", json={
        "email": "wrong@knowai.dev",
        "password": "incorrect",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"].endswith("@knowai.dev")
    assert resp.json()["display_name"] == "Test User"


@pytest.mark.asyncio
async def test_refresh(client: AsyncClient):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "refresh@knowai.dev",
        "username": "refreshuser",
        "password": "pass123",
    })
    refresh_token = reg.json()["refresh_token"]
    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()
