from __future__ import annotations
import sys
from pathlib import Path
import base64
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).parents[1]))

from archon.output.github_adr import commit_adrs_to_github
from archon.core.models.artifact import Artifact, ArtifactType


def _pkg_with_adr(sample_package):
    sample_package.artifacts = [
        Artifact(
            id="adr-001",
            artifact_type=ArtifactType.ADR,
            title="Use PostgreSQL",
            content="# ADR-001\nDecision: use PostgreSQL",
            filename="adr-001.md",
        )
    ]
    return sample_package


@pytest.mark.asyncio
async def test_commit_adrs_base64_encodes_content(sample_package):
    pkg = _pkg_with_adr(sample_package)
    put_payloads = []

    async def fake_get(url, headers=None):
        m = MagicMock()
        m.status_code = 404
        return m

    async def fake_put(url, json=None, headers=None):
        put_payloads.append(json)
        m = MagicMock()
        m.status_code = 201
        return m

    mock_client = AsyncMock()
    mock_client.get = fake_get
    mock_client.put = fake_put
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", return_value=mock_client), \
         patch.dict("os.environ", {"GITHUB_TOKEN": "tok"}):
        paths = await commit_adrs_to_github(pkg, "test/repo")

    assert len(paths) == 1
    assert "docs/adr/adr-001.md" in paths[0]
    raw = base64.b64decode(put_payloads[0]["content"]).decode("utf-8")
    assert "ADR-001" in raw


@pytest.mark.asyncio
async def test_commit_adrs_includes_sha_for_existing_file(sample_package):
    pkg = _pkg_with_adr(sample_package)
    put_payloads = []

    async def fake_get(url, headers=None):
        m = MagicMock()
        m.status_code = 200
        m.json.return_value = {"sha": "existing-sha-abc"}
        return m

    async def fake_put(url, json=None, headers=None):
        put_payloads.append(json)
        m = MagicMock()
        m.status_code = 200
        return m

    mock_client = AsyncMock()
    mock_client.get = fake_get
    mock_client.put = fake_put
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", return_value=mock_client), \
         patch.dict("os.environ", {"GITHUB_TOKEN": "tok"}):
        await commit_adrs_to_github(pkg, "test/repo")

    assert put_payloads[0]["sha"] == "existing-sha-abc"


@pytest.mark.asyncio
async def test_commit_adrs_returns_empty_for_no_adrs(sample_package):
    sample_package.artifacts = []
    with patch.dict("os.environ", {"GITHUB_TOKEN": "tok"}):
        result = await commit_adrs_to_github(sample_package, "test/repo")
    assert result == []


@pytest.mark.asyncio
async def test_commit_adrs_raises_without_token(sample_package):
    pkg = _pkg_with_adr(sample_package)
    with patch.dict("os.environ", {}, clear=True):
        import os
        os.environ.pop("GITHUB_TOKEN", None)
        with pytest.raises(EnvironmentError):
            await commit_adrs_to_github(pkg, "test/repo")
