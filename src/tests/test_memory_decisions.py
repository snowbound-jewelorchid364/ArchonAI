from __future__ import annotations
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from archon.memory.decisions import save_decisions, _extract_section
from archon.core.models.artifact import ArtifactType, Artifact
from archon.core.models.review_package import ReviewPackage


def _make_package(artifacts=None, repo_url="https://github.com/test/repo"):
    return ReviewPackage(
        run_id=str(uuid.uuid4()),
        repo_url=repo_url,
        mode="review",
        artifacts=artifacts or [],
        duration_seconds=1.0,
        executive_summary="",
    )


def _adr_artifact(title="ADR-001: Use PostgreSQL", content="## Decision\nWe chose PostgreSQL.\n## Rationale\nReliability.") -> Artifact:
    return Artifact(
        id=str(uuid.uuid4()),
        artifact_type=ArtifactType.ADR,
        title=title,
        content=content,
        filename="adr-001.md",
    )


def _terraform_artifact() -> Artifact:
    return Artifact(
        id=str(uuid.uuid4()),
        artifact_type=ArtifactType.TERRAFORM,
        title="main.tf",
        content="resource aws_s3_bucket {}",
        filename="main.tf",
    )


@pytest.mark.asyncio
async def test_save_decisions_saves_adr():
    db = AsyncMock()
    db.add = MagicMock()
    pkg = _make_package([_adr_artifact()])
    await save_decisions(db, "u1", "r1", pkg)
    db.add.assert_called_once()
    row = db.add.call_args[0][0]
    assert row.adr_title == "ADR-001: Use PostgreSQL"
    assert "PostgreSQL" in row.decision


@pytest.mark.asyncio
async def test_save_decisions_skips_non_adr():
    db = AsyncMock()
    db.add = MagicMock()
    pkg = _make_package([_terraform_artifact()])
    await save_decisions(db, "u1", "r1", pkg)
    db.add.assert_not_called()


def test_extract_section_finds_heading():
    md = "## Decision\nWe chose X.\n## Rationale\nBecause Y."
    result = _extract_section(md, "Decision")
    assert result == "We chose X."


def test_extract_section_missing_heading_returns_empty():
    md = "## Rationale\nBecause Y."
    result = _extract_section(md, "Decision")
    assert result == ""
