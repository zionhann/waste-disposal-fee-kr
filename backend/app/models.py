from pydantic import BaseModel


class SearchResult(BaseModel):
    name: str
    category: str
    spec: str
    fee: int
    similarity: float
    sido: str
    sigungu: str


class SearchResponse(BaseModel):
    results: list[SearchResult]
