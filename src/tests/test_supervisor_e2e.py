from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from archon.core.models import AgentOutput, Finding, ReviewPackage, Severity
from archon.engine.supervisor import Supervisor


def _finding(domain: str, title: str = "Issue") -> Finding:
    return Finding(
        id=str(uuid.uuid4()),
        title=title,
        description="desc",
        severity=Severity.HIGH,
        domain=domain,
        recommendation="fix",
        confidence=0.9,
    )


def _output(domain: str, finding: Finding) -> AgentOutput:
    return AgentOutput(
        domain=domain,
        findings=[finding],
        confidence=0.9,
        duration_seconds=0.1,
    )


@pytest.mark.asyncio
async def test_supervisor_run_merges_six_domains() -> None:
    llm = AsyncMock()
    llm.complete = AsyncMock(return_value="Executive summary")
    supervisor = Supervisor(llm, [MagicMock()], MagicMock())

    domains = [
        "software-architect",
        "cloud-architect",
        "security-architect",
        "data-architect",
        "integration-architect",
        "ai-architect",
    ]

    agents = []
    for d in domains:
        a = MagicMock()
        a.domain = d
        a.run = AsyncMock(return_value=_output(d, _finding(d, f"{d} finding")))
        agents.append(a)

    with patch.object(supervisor, "_build_agents", return_value=agents):
        package = await supervisor.run("brief: b2b saas", "review")

    assert isinstance(package, ReviewPackage)
    assert len(package.findings) >= 6
    assert package.executive_summary
    present = {f.domain for f in package.findings}
    for d in domains:
        assert d in present


@pytest.mark.asyncio
async def test_supervisor_deduplicates_identical_findings_across_agents() -> None:
    llm = AsyncMock()
    llm.complete = AsyncMock(return_value="Summary")
    supervisor = Supervisor(llm, [MagicMock()], MagicMock())

    duplicate_title = "Duplicate Risk"
    f1 = _finding("software-architect", duplicate_title)
    f2 = _finding("cloud-architect", duplicate_title)

    a1 = MagicMock()
    a1.domain = "software-architect"
    a1.run = AsyncMock(return_value=_output("software-architect", f1))

    a2 = MagicMock()
    a2.domain = "cloud-architect"
    a2.run = AsyncMock(return_value=_output("cloud-architect", f2))

    with patch.object(supervisor, "_build_agents", return_value=[a1, a2]):
        package = await supervisor.run("brief: same issue", "review")

    dup_matches = [f for f in package.findings if f.title == duplicate_title]
    assert len(dup_matches) == 1
