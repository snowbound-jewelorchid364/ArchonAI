"""Tests for TavilyAdapter — search, rate limit, network error."""
from __future__ import annotations
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx


@pytest.fixture
def adapter():
    with patch("archon.infrastructure.search.tavily_adapter.settings") as mock_settings:
        mock_settings.tavily_api_key = "test-tavily-key"
        from archon.infrastructure.search.tavily_adapter import TavilyAdapter
        a = TavilyAdapter.__new__(TavilyAdapter)
        a._api_key = "test-tavily-key"
        return a


def _mock_response(status_code: int, json_data: dict):
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status = MagicMock()
    if status_code >= 400:
        resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            message=f"{status_code}", request=MagicMock(), response=resp
        )
    return resp


@pytest.mark.asyncio
async def test_search_returns_results(adapter):
    """Successful search returns list of SearchResult."""
    json_data = {
        "results": [
            {
                "url": "https://example.com/article",
                "title": "Test Article",
                "content": "This is a test excerpt about architecture.",
                "published_date": "2024-01-15",
                "score": 0.95,
            }
        ]
    }
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=_mock_response(200, json_data))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", return_value=mock_client):
        results = await adapter.search("architecture patterns", max_results=5)

    assert len(results) == 1
    assert results[0].title == "Test Article"
    assert str(results[0].url) == "https://example.com/article"
    assert results[0].score == 0.95


@pytest.mark.asyncio
async def test_search_returns_empty_on_rate_limit(adapter):
    """429 rate limit returns empty list."""
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=_mock_response(429, {}))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", return_value=mock_client):
        results = await adapter.search("test query")

    assert results == []


@pytest.mark.asyncio
async def test_search_returns_empty_on_network_error(adapter):
    """Network error returns empty list."""
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(side_effect=httpx.ConnectError("connection refused"))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", return_value=mock_client):
        results = await adapter.search("test query")

    assert results == []


@pytest.mark.asyncio
async def test_search_handles_empty_results(adapter):
    """API returns empty results array."""
    json_data = {"results": []}
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=_mock_response(200, json_data))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", return_value=mock_client):
        results = await adapter.search("obscure query that returns nothing")

    assert results == []
