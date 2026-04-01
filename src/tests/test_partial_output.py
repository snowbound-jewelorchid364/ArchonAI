from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from archon.core.models import AgentOutput, Finding, Severity
from archon.engine.supervisor import Supervisor


def _ok_output(domain: str) -> AgentOutput:
    finding = Finding(
        id=str(uuid.uuid4()),
        title=f"{domain} finding",
        description="desc",
        severity=Severity.HIGH,
        domain=domain,
        recommendation="fix",
        confidence=0.8,
    )
    return AgentOutput(domain=domain, findings=[finding], confidence=0.8, duration_seconds=0.1)


@pytest.mark.asyncio
async def test_supervisor_partial_output_when_one_agent_raises() -> None:
    llm = MagicMock()
    llm.complete = AsyncMock(return_value="Summary")
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
    for i, d in enumerate(domains):
        a = MagicMock()
        a.domain = d
        if i == 2:
            a.run = AsyncMock(side_effect=RuntimeError("AgentError: failed"))
        else:
            a.run = AsyncMock(return_value=_ok_output(d))
        agents.append(a)

    with patch.object(supervisor, "_build_agents", return_value=agents):
        package = await supervisor.run("https://github.com/test/repo", "review")

    assert package.partial is True
    assert len(package.findings) == 5
    assert package.agent_statuses["security-architect"] == "FAILED"
