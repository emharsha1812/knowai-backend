from pydantic import BaseModel


class SearchResult(BaseModel):
    content_type: str   # writing_post | course | lesson | problem | concept
    id: int
    slug: str
    title: str
    snippet: str | None  # headline excerpt from pg ts_headline
    rank: float


class SearchResponse(BaseModel):
    query: str
    total: int
    results: list[SearchResult]
