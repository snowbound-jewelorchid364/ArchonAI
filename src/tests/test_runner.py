from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest

from archon.core.models import Finding, ReviewPackage, Severity
from archon.engine.runner import Runner
from archon.engine.hitl.checkpoints import HITLMode
from archon.core.models.job import JobStatus


def _package(partial: bool = False) -> ReviewPackage:
    finding = Finding(
        id=str(uuid.uuid4()),
        title="Runner finding",
        description="desc",
        severity=Severity.HIGH,
        domain="software-architect",
        recommendation="fix",
        confidence=0.8,
    )
    return ReviewPackage(
        run_id=str(uuid.uuid4()),
        repo_url="https://github.com/test/repo",
        mode="review",
        duration_seconds=1.0,
        executive_summary="summary",
        findings=[finding],
        partial=partial,
    )


@pytest.mark.asyncio
async def test_runner_status_completed_on_success() -> None:
    supervisor = AsyncMock()
    supervisor.run = AsyncMock(return_value=_package(partial=False))
    runner = Runner(supervisor)

    job, package = await runner.run("https://github.com/test/repo", "review")

    assert package.partial is False
    assert job.status == JobStatus.COMPLETED
    assert job.finding_count == 1


@pytest.mark.asyncio
async def test_runner_status_failed_on_exception() -> None:
    supervisor = AsyncMock()
    supervisor.run = AsyncMock(side_effect=RuntimeError("boom"))
    runner = Runner(supervisor)

    with pytest.raises(RuntimeError, match="boom"):
        await runner.run("https://github.com/test/repo", "review")


@pytest.mark.asyncio
async def test_runner_status_partial_when_supervisor_returns_partial_package() -> None:
    supervisor = AsyncMock()
    supervisor.run = AsyncMock(return_value=_package(partial=True))
    runner = Runner(supervisor)

    job, package = await runner.run(
        "https://github.com/test/repo",
        "review",
        hitl_mode=HITLMode.AUTOPILOT,
    )

    assert package.partial is True
    assert job.status == JobStatus.PARTIAL


@pytest.mark.asyncio
async def test_runner_handles_timeout_as_failure_when_not_converted_upstream() -> None:
    supervisor = AsyncMock()
    supervisor.run = AsyncMock(side_effect=TimeoutError("timeout"))
    runner = Runner(supervisor)

    with pytest.raises(TimeoutError):
        await runner.run("https://github.com/test/repo", "review")
