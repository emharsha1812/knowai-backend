from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.schemas.search import SearchResult, SearchResponse


_SEARCH_SQL = text("""
WITH results AS (
    SELECT
        'writing_post' AS content_type,
        id,
        slug,
        title,
        ts_headline('english', content, query, 'MaxWords=25, MinWords=10') AS snippet,
        ts_rank(search_vector, query)                                       AS rank
    FROM writing_posts, plainto_tsquery('english', :q) AS query
    WHERE is_published = true AND search_vector @@ query

    UNION ALL

    SELECT
        'course'       AS content_type,
        id,
        slug,
        title,
        ts_headline('english', description, query, 'MaxWords=25, MinWords=10') AS snippet,
        ts_rank(search_vector, query) AS rank
    FROM courses, plainto_tsquery('english', :q) AS query
    WHERE is_published = true AND search_vector @@ query

    UNION ALL

    SELECT
        'lesson'       AS content_type,
        id,
        slug,
        title,
        ts_headline('english', content, query, 'MaxWords=25, MinWords=10') AS snippet,
        ts_rank(search_vector, query) AS rank
    FROM lessons, plainto_tsquery('english', :q) AS query
    WHERE is_published = true AND search_vector @@ query

    UNION ALL

    SELECT
        'problem'      AS content_type,
        id,
        slug,
        title,
        ts_headline('english', description, query, 'MaxWords=25, MinWords=10') AS snippet,
        ts_rank(search_vector, query) AS rank
    FROM problems, plainto_tsquery('english', :q) AS query
    WHERE is_published = true AND search_vector @@ query

    UNION ALL

    SELECT
        'concept'      AS content_type,
        id,
        slug,
        title,
        ts_headline('english', body, query, 'MaxWords=25, MinWords=10') AS snippet,
        ts_rank(search_vector, query) AS rank
    FROM concepts, plainto_tsquery('english', :q) AS query
    WHERE is_published = true AND search_vector @@ query
)
SELECT * FROM results
ORDER BY rank DESC
LIMIT :limit OFFSET :offset;
""")


async def full_text_search(
    db: AsyncSession,
    query: str,
    limit: int = 20,
    offset: int = 0,
) -> SearchResponse:
    rows = await db.execute(_SEARCH_SQL, {"q": query, "limit": limit, "offset": offset})
    results = [
        SearchResult(
            content_type=row.content_type,
            id=row.id,
            slug=row.slug,
            title=row.title,
            snippet=row.snippet,
            rank=float(row.rank),
        )
        for row in rows
    ]
    return SearchResponse(query=query, total=len(results), results=results)
