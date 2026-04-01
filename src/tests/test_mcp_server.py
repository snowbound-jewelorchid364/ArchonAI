from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from archon.mcp import server as mcp_server


@pytest.mark.asyncio
async def test_review_repo_calls_api() -> None:
    with patch("archon.mcp.server._request_json", new_callable=AsyncMock) as req:
        req.return_value = {"review_id": "r1", "job_id": "j1", "status": "QUEUED"}
        out = await mcp_server.review_repo("https://github.com/o/r", "review")

    req.assert_awaited_once_with(
        "POST",
        "/api/v1/reviews",
        json_body={"repo_url": "https://github.com/o/r", "mode": "review"},
    )
    assert out["job_id"] == "j1"


@pytest.mark.asyncio
async def test_get_findings_filters_by_severity() -> None:
    data = {
        "findings": [
            {"id": "1", "severity": "CRITICAL", "title": "c"},
            {"id": "2", "severity": "HIGH", "title": "h"},
            {"id": "3", "severity": "LOW", "title": "l"},
        ]
    }
    with patch("archon.mcp.server._request_json", new_callable=AsyncMock) as req:
        req.return_value = data
        out = await mcp_server.get_findings("rev-1", "high")
    assert len(out) == 1
    assert out[0]["severity"] == "HIGH"


class _FakeStreamResponse:
    def __init__(self, lines: list[str]) -> None:
        self._lines = lines

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def raise_for_status(self) -> None:
        return None

    async def aiter_lines(self):
        for line in self._lines:
            yield line


class _FakeAsyncClient:
    def __init__(self, *args, **kwargs) -> None:
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def stream(self, *args, **kwargs):
        lines = [
            "data: " + json.dumps({"type": "text", "data": "Hello "}),
            "data: " + json.dumps({"type": "text", "data": "ARCHON"}),
            "data: " + json.dumps({"type": "done", "data": ""}),
        ]
        return _FakeStreamResponse(lines)


@pytest.mark.asyncio
async def test_ask_architecture_returns_string() -> None:
    with patch("archon.mcp.server.httpx.AsyncClient", _FakeAsyncClient):
        out = await mcp_server.ask_architecture("rev-1", "What should I fix?")
    assert out == "Hello ARCHON"


@pytest.mark.asyncio
async def test_get_health_score_returns_dict() -> None:
    with patch("archon.mcp.server._request_json", new_callable=AsyncMock) as req:
        req.return_value = {
            "repo_url": "https://github.com/o/r",
            "overall": 88.5,
            "domains": {"security": 80},
            "created_at": "2026-01-01T00:00:00Z",
        }
        out = await mcp_server.get_health_score("https://github.com/o/r")
    assert out["overall"] == 88.5
    assert "domains" in out


@pytest.mark.asyncio
async def test_get_adrs_returns_list() -> None:
    with patch("archon.mcp.server._request_json", new_callable=AsyncMock) as req:
        req.return_value = {
            "package_json": {
                "artifacts": [
                    {"artifact_type": "ADR", "title": "ADR-001", "content": "Use X"},
                    {"artifact_type": "DIAGRAM", "title": "D", "content": "graph TD"},
                ]
            }
        }
        out = await mcp_server.get_adrs("rev-1")
    assert out == [{"title": "ADR-001", "content": "Use X"}]


def test_mcp_tools_registered() -> None:
    expected = {
        "review_repo",
        "get_findings",
        "ask_architecture",
        "get_health_score",
        "get_adrs",
    }
    assert expected.issubset(set(mcp_server.REGISTERED_TOOLS))
