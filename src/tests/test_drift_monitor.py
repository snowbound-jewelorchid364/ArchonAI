from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from archon.core.models import ReviewPackage
from archon.engine.modes.drift_monitor import DriftInput, build_drift_focus
from archon.output.sections.drift_monitor import render_drift_monitor
from archon.workers import drift_worker


def _package_json() -> dict:
    return ReviewPackage(
        run_id="r1",
        repo_url="https://github.com/o/r",
        mode="drift_monitor",
        duration_seconds=1.0,
        executive_summary="drift",
        findings=[],
        artifacts=[],
        citations=[],
        agent_statuses={},
        partial=False,
        model_version="test",
    ).model_dump(mode="json")


def test_build_drift_focus_references_snapshot() -> None:
    focus = build_drift_focus(DriftInput(repo_url="https://github.com/o/r", previous_snapshot_id="snap-123"))
    assert "snap-123" in focus


def test_render_drift_monitor_has_all_sections() -> None:
    pkg = ReviewPackage(
        run_id="r1",
        repo_url="https://github.com/o/r",
        mode="drift_monitor",
        duration_seconds=1.0,
        executive_summary="drift",
        findings=[],
        artifacts=[],
        citations=[],
        agent_statuses={},
        partial=False,
        model_version="test",
    )
    out = render_drift_monitor(pkg)
    assert "### New Components" in out
    assert "### Removed Components" in out
    assert "### Changed Interfaces" in out
    assert "### New Security Exposures" in out
    assert "### Cost Impact" in out


@pytest.mark.asyncio
async def test_drift_worker_fetches_previous_snapshot() -> None:
    fake_snapshot = SimpleNamespace(id="s1", summary="old")

    class _Session:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, model, review_id):
            return None

        async def commit(self):
            return None

    with patch("archon.workers.drift_worker.get_session", return_value=_Session()):
        with patch("archon.workers.drift_worker.get_snapshots", new_callable=AsyncMock) as gs:
            gs.return_value = [fake_snapshot]
            with patch("archon.workers.drift_worker.process_review", new_callable=AsyncMock) as pr:
                await drift_worker.run_drift_check("https://github.com/o/r", "u1")

    gs.assert_awaited()
    pr.assert_awaited()


@pytest.mark.asyncio
async def test_drift_worker_saves_new_snapshot_on_completion() -> None:
    review_row = SimpleNamespace(package_json=_package_json())

    class _Session:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, model, review_id):
            return review_row

        async def commit(self):
            return None

    with patch("archon.workers.drift_worker.get_session", return_value=_Session()):
        with patch("archon.workers.drift_worker.get_snapshots", new_callable=AsyncMock) as gs:
            gs.return_value = []
            with patch("archon.workers.drift_worker.process_review", new_callable=AsyncMock):
                with patch("archon.workers.drift_worker.save_snapshot", new_callable=AsyncMock) as ss:
                    await drift_worker.run_drift_check("https://github.com/o/r", "u1")

    ss.assert_awaited()
