import pytest
import pytest_asyncio
from uuid import uuid4
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"


@compiles(TSVECTOR, "sqlite")
def compile_tsvector_sqlite(type_, compiler, **kw):
    return "TEXT"


# Use an in-memory SQLite database for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient) -> dict:
    """Register a test user and return auth headers."""
    suffix = uuid4().hex
    resp = await client.post("/api/v1/auth/register", json={
        "email": f"test-{suffix}@knowai.dev",
        "username": f"testuser-{suffix}",
        "password": "testpassword123",
        "display_name": "Test User",
    })
    assert resp.status_code == 201
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_headers(client: AsyncClient) -> dict:
    """Register a user and promote to admin, then return auth headers."""
    from sqlalchemy import update
    from app.models.user import User, UserRole

    suffix = uuid4().hex
    email = f"admin-{suffix}@knowai.dev"
    resp = await client.post("/api/v1/auth/register", json={
        "email": email,
        "username": f"adminuser-{suffix}",
        "password": "adminpassword123",
    })
    assert resp.status_code == 201
    token = resp.json()["access_token"]

    # Directly update role in test DB
    async with TestSessionLocal() as session:
        await session.execute(
            update(User).where(User.email == email).values(role=UserRole.admin)
        )
        await session.commit()

    # Re-login to get a fresh token
    login = await client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "adminpassword123",
    })
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
