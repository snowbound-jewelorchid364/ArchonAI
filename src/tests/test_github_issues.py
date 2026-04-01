from __future__ import annotations
import sys
from pathlib import Path
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).parents[1]))

from archon.output.github_issues import push_findings_to_github


@pytest.mark.asyncio
async def test_push_findings_calls_github_api(sample_package):
    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {"html_url": "https://github.com/test/repo/issues/1"}

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", return_value=mock_client), \
         patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"}):
        urls = await push_findings_to_github(sample_package, "test/repo", "https://archon.ai/share/abc")

    assert len(urls) > 0
    assert "https://github.com/test/repo/issues/1" in urls


@pytest.mark.asyncio
async def test_push_findings_only_high_plus(sample_package):
    call_bodies = []

    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {"html_url": "https://github.com/test/repo/issues/99"}

    async def capture_post(url, json=None, headers=None):
        call_bodies.append(json)
        return mock_resp

    mock_client = AsyncMock()
    mock_client.post = capture_post
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", return_value=mock_client), \
         patch.dict("os.environ", {"GITHUB_TOKEN": "tok"}):
        await push_findings_to_github(sample_package, "test/repo")

    severities = [b["labels"][0].upper() for b in call_bodies]
    assert all(s in ("critical", "high") for s in [b["labels"][0] for b in call_bodies])


@pytest.mark.asyncio
async def test_push_findings_raises_without_token(sample_package):
    with patch.dict("os.environ", {}, clear=True):
        import os
        os.environ.pop("GITHUB_TOKEN", None)
        with pytest.raises(EnvironmentError):
            await push_findings_to_github(sample_package, "test/repo")


@pytest.mark.asyncio
async def test_push_findings_labels_include_archon(sample_package):
    captured = []
    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {"html_url": "https://github.com/x/y/issues/1"}

    async def cap(url, json=None, headers=None):
        captured.append(json)
        return mock_resp

    mock_client = AsyncMock()
    mock_client.post = cap
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", return_value=mock_client), \
         patch.dict("os.environ", {"GITHUB_TOKEN": "tok"}):
        await push_findings_to_github(sample_package, "test/repo")

    for body in captured:
        assert "archon" in body["labels"]
