FRONTEND_COURSE_CATALOG: list[dict] = []

CATALOG_BY_SLUG: dict[str, dict] = {}
LESSON_BY_SLUG: dict[str, dict] = {}


def catalog_course_summaries(
    *,
    difficulty: str | None = None,
    exclude_slugs: set[str] | None = None,
) -> list[dict]:
    exclude_slugs = exclude_slugs or set()
    return [
        {
            "id": course["id"],
            "slug": course["slug"],
            "title": course["title"],
            "subtitle": course["subtitle"],
            "difficulty": course["difficulty"],
            "tags": course["tags"],
            "estimated_hours": course["estimated_hours"],
            "is_published": course["is_published"],
            "created_at": course["created_at"],
        }
        for course in FRONTEND_COURSE_CATALOG
        if course["slug"] not in exclude_slugs
        and (difficulty is None or course["difficulty"] == difficulty)
    ]
