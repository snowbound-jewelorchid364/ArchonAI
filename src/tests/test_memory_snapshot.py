from __future__ import annotations
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from archon.memory.snapshot import save_snapshot, build_memory_context
from archon.core.models.finding import Finding, Severity
from archon.core.models.review_package import ReviewPackage


def _make_package(findings=None, repo_url="https://github.com/test/repo", mode="review"):
    return ReviewPackage(
        run_id=str(uuid.uuid4()),
        repo_url=repo_url,
        mode=mode,
        findings=findings or [],
        duration_seconds=5.0,
        executive_summary="Looks good.",
    )


def _finding(domain: str, severity: Severity) -> Finding:
    return Finding(
        id=str(uuid.uuid4()),
        title="Issue",
        description="desc",
        severity=severity,
        domain=domain,
        recommendation="fix",
        confidence=0.9,
    )


@pytest.mark.asyncio
async def test_save_snapshot_persists_fields():
    db = AsyncMock()
    db.add = MagicMock()
    pkg = _make_package([_finding("security", Severity.CRITICAL)])
    await save_snapshot(db, "user1", "rev1", pkg)
    db.add.assert_called_once()
    row = db.add.call_args[0][0]
    assert row.user_id == "user1"
    assert row.review_id == "rev1"
    assert row.repo_url == "https://github.com/test/repo"
    assert row.finding_count == 1
    assert row.critical_count == 1


@pytest.mark.asyncio
async def test_save_snapshot_domains_json_counts():
    db = AsyncMock()
    db.add = MagicMock()
    findings = [
        _finding("security", Severity.HIGH),
        _finding("security", Severity.MEDIUM),
        _finding("cloud", Severity.LOW),
    ]
    pkg = _make_package(findings)
    await save_snapshot(db, "u", "r", pkg)
    row = db.add.call_args[0][0]
    assert row.domains_json["security"] == 2
    assert row.domains_json["cloud"] == 1


@pytest.mark.asyncio
async def test_build_memory_context_empty_when_no_history():
    with patch("archon.memory.snapshot.get_snapshots", AsyncMock(return_value=[])):
        with patch("archon.memory.snapshot.get_decisions", AsyncMock(return_value=[])):
            result = await build_memory_context(MagicMock(), "user1", "https://github.com/x/y")
    assert result == ""


@pytest.mark.asyncio
async def test_build_memory_context_contains_history_header():
    from db.models import ArchitectureSnapshotRow
    from datetime import datetime, UTC
    snap = ArchitectureSnapshotRow(
        id="s1", user_id="u1", review_id="r1",
        repo_url="https://github.com/x/y",
        mode="review", summary="All good.",
        finding_count=2, critical_count=0, high_count=1,
        domains_json={"security": 1},
        created_at=datetime.now(UTC),
    )
    with patch("archon.memory.snapshot.get_snapshots", AsyncMock(return_value=[snap])):
        with patch("archon.memory.snapshot.get_decisions", AsyncMock(return_value=[])):
            result = await build_memory_context(MagicMock(), "u1", "https://github.com/x/y")
    assert "## Architecture History" in result
    assert "All good." in result


@pytest.mark.asyncio
async def test_build_memory_context_includes_decisions():
    from db.models import ArchitectureSnapshotRow, DecisionHistoryRow
    from datetime import datetime, UTC
    snap = ArchitectureSnapshotRow(
        id="s1", user_id="u1", review_id="r1",
        repo_url="https://github.com/x/y",
        mode="review", summary="Review done.",
        finding_count=1, critical_count=1, high_count=0,
        domains_json={},
        created_at=datetime.now(UTC),
    )
    dec = DecisionHistoryRow(
        id="d1", user_id="u1", review_id="r1",
        repo_url="https://github.com/x/y",
        adr_title="Use PostgreSQL",
        decision="We chose PostgreSQL.",
        rationale="Reliability.",
        status="active",
        created_at=datetime.now(UTC),
    )
    with patch("archon.memory.snapshot.get_snapshots", AsyncMock(return_value=[snap])):
        with patch("archon.memory.snapshot.get_decisions", AsyncMock(return_value=[dec])):
            result = await build_memory_context(MagicMock(), "u1", "https://github.com/x/y")
    assert "Use PostgreSQL" in result
