from __future__ import annotations
import sys
from pathlib import Path
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).parents[1]))

from archon.output.slack_notifier import send_slack_digest, _build_blocks


def test_build_blocks_structure(sample_package):
    blocks = _build_blocks(sample_package, "https://archon.ai/share/abc")
    assert len(blocks) == 3
    assert blocks[0]["type"] == "header"
    assert blocks[1]["type"] == "section"
    assert blocks[2]["type"] == "actions"


def test_build_blocks_no_share_url(sample_package):
    blocks = _build_blocks(sample_package)
    assert len(blocks) == 2
    assert blocks[-1]["type"] == "section"


def test_build_blocks_contains_health_score(sample_package):
    blocks = _build_blocks(sample_package)
    fields_text = " ".join(f["text"] for f in blocks[1]["fields"])
    assert "Health Score" in fields_text


def test_build_blocks_contains_repo_name(sample_package):
    blocks = _build_blocks(sample_package)
    header_text = blocks[0]["text"]["text"]
    assert "repo" in header_text.lower()


@pytest.mark.asyncio
async def test_send_slack_digest_success(sample_package):
    mock_resp = MagicMock()
    mock_resp.status_code = 200

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await send_slack_digest(sample_package, "https://hooks.slack.com/test")

    assert result is True


@pytest.mark.asyncio
async def test_send_slack_digest_failure(sample_package):
    mock_resp = MagicMock()
    mock_resp.status_code = 400
    mock_resp.text = "invalid_payload"

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await send_slack_digest(sample_package, "https://hooks.slack.com/test")

    assert result is False
