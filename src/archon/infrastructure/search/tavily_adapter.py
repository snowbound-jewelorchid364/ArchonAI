from __future__ import annotations
import logging
import httpx
from ...core.ports.search_port import SearchPort, SearchResult
from ...config.settings import settings

logger = logging.getLogger(__name__)


class TavilyAdapter(SearchPort):
    _BASE_URL = "https://api.tavily.com/search"

    async def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    self._BASE_URL,
                    json={"api_key": settings.tavily_api_key, "query": query, "max_results": max_results},
                )
                response.raise_for_status()
                data = response.json()
            return [
                SearchResult(
                    url=r["url"],
                    title=r.get("title", ""),
                    excerpt=r.get("content", "")[:300],
                    published_date=r.get("published_date"),
                    score=r.get("score", 0.5),
                )
                for r in data.get("results", [])
            ]
        except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException, Exception) as e:
            logger.warning("Tavily search failed: %s", e)
            return []
