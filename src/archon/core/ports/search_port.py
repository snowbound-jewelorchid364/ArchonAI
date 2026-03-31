from __future__ import annotations
from abc import ABC, abstractmethod
from pydantic import BaseModel, HttpUrl


class SearchResult(BaseModel):
    url: HttpUrl
    title: str
    excerpt: str
    published_date: str | None = None
    score: float = 0.0


class SearchPort(ABC):
    @abstractmethod
    async def search(self, query: str, max_results: int = 5) -> list[SearchResult]: ...
