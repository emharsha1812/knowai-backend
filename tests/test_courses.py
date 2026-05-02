import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_course_and_structure(client: AsyncClient, admin_headers: dict):
    # Create course
    resp = await client.post("/api/v1/courses", headers=admin_headers, json={
        "slug": "transformers-ground-up",
        "title": "Transformers from the Ground Up",
        "description": "Build a transformer from scratch step by step.",
        "difficulty": "advanced",
        "is_published": True,
    })
    assert resp.status_code == 201
    course_slug = resp.json()["slug"]

    # Add chapter
    resp = await client.post(f"/api/v1/courses/{course_slug}/chapters", headers=admin_headers, json={
        "title": "Chapter 1: Attention",
        "order": 1,
    })
    assert resp.status_code == 201
    chapter_id = resp.json()["id"]

    # Add lesson
    resp = await client.post(f"/api/v1/courses/chapters/{chapter_id}/lessons", headers=admin_headers, json={
        "slug": "scaled-dot-product",
        "title": "Scaled Dot-Product Attention",
        "content": "## Scaled Dot-Product Attention\n...",
        "order": 1,
        "is_published": True,
    })
    assert resp.status_code == 201

    # Get full course with chapters and lessons
    resp = await client.get(f"/api/v1/courses/{course_slug}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["chapters"]) == 1
    assert data["chapters"][0]["lessons"][0]["slug"] == "scaled-dot-product"


@pytest.mark.asyncio
async def test_get_lesson_by_slug(client: AsyncClient, admin_headers: dict):
    await client.post("/api/v1/courses", headers=admin_headers, json={
        "slug": "course-lesson-test",
        "title": "Course",
        "description": "Test",
        "difficulty": "beginner",
        "is_published": True,
    })
    ch = await client.post("/api/v1/courses/course-lesson-test/chapters", headers=admin_headers, json={
        "title": "Ch1",
        "order": 1,
    })
    chapter_id = ch.json()["id"]
    await client.post(f"/api/v1/courses/chapters/{chapter_id}/lessons", headers=admin_headers, json={
        "slug": "lesson-slug-test",
        "title": "My Lesson",
        "content": "Content",
        "order": 1,
        "is_published": True,
    })
    resp = await client.get("/api/v1/courses/lessons/lesson-slug-test")
    assert resp.status_code == 200
    assert resp.json()["title"] == "My Lesson"


@pytest.mark.asyncio
async def test_frontend_course_catalog_fallbacks(client: AsyncClient):
    resp = await client.get("/api/v1/courses/math-for-ml")
    assert resp.status_code == 200
    data = resp.json()
    assert data["slug"] == "math-for-ml"
    assert data["chapters"]
    assert data["chapters"][0]["lessons"][0]["slug"] == "vectors-and-bases"


@pytest.mark.asyncio
async def test_frontend_lesson_catalog_fallback(client: AsyncClient):
    resp = await client.get("/api/v1/courses/lessons/kv-cache-mental-model")
    assert resp.status_code == 200
    data = resp.json()
    assert data["slug"] == "kv-cache-mental-model"
    assert data["is_published"] is True


@pytest.mark.asyncio
async def test_list_courses_includes_frontend_catalog(client: AsyncClient):
    resp = await client.get("/api/v1/courses?page=1&page_size=30")
    assert resp.status_code == 200
    slugs = {course["slug"] for course in resp.json()}
    assert {"deep-learning", "math-for-ml", "inference", "vision"}.issubset(slugs)
