from __future__ import annotations
import httpx
from ...core.ports.search_port import SearchPort, SearchResult
from ...config.settings import settings


class ExaAdapter(SearchPort):
    _BASE_URL = "https://api.exa.ai/search"

    async def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                self._BASE_URL,
                headers={"x-api-key": settings.exa_api_key, "Content-Type": "application/json"},
                json={"query": query, "numResults": max_results, "useAutoprompt": True, "contents": {"text": {"maxCharacters": 300}}},
            )
            response.raise_for_status()
            data = response.json()
        return [
            SearchResult(
                url=r["url"],
                title=r.get("title", ""),
                excerpt=(r.get("text") or "")[:300],
                published_date=r.get("publishedDate"),
                score=r.get("score", 0.5),
            )
            for r in data.get("results", [])
        ]
