from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from archon.core.models import AgentOutput, Finding, Severity
from archon.engine.hitl.checkpoints import CheckpointType, HITLMode
from archon.engine.supervisor import Supervisor


def _output(domain: str) -> AgentOutput:
    finding = Finding(
        id=f"{domain}-1",
        title=f"{domain} finding",
        description="desc",
        severity=Severity.MEDIUM,
        domain=domain,
        recommendation="fix",
        confidence=0.8,
    )
    return AgentOutput(domain=domain, findings=[finding], confidence=0.8, duration_seconds=0.1)


@pytest.mark.asyncio
async def test_supervised_mode_checkpoints_fire_in_order() -> None:
    llm = MagicMock()
    llm.complete = AsyncMock(return_value="Summary")
    supervisor = Supervisor(llm, [MagicMock()], MagicMock())

    domains = ["software-architect", "cloud-architect"]
    agents = []
    for d in domains:
        a = MagicMock()
        a.domain = d
        a.run = AsyncMock(return_value=_output(d))
        agents.append(a)

    seen: list[str] = []

    async def on_checkpoint(cp) -> None:
        seen.append(cp.type.value)
        cp.approved = True

    with patch.object(supervisor, "_build_agents", return_value=agents):
        await supervisor.run(
            "https://github.com/test/repo",
            "due_diligence",
            hitl_mode=HITLMode.SUPERVISED,
            on_checkpoint=on_checkpoint,
        )

    assert seen == [
        CheckpointType.AGENTS_STARTED.value,
        CheckpointType.FINDINGS_READY.value,
        CheckpointType.PACKAGE_READY.value,
    ]


@pytest.mark.asyncio
async def test_supervised_path_continues_after_each_checkpoint_approval() -> None:
    llm = MagicMock()
    llm.complete = AsyncMock(return_value="Summary")
    supervisor = Supervisor(llm, [MagicMock()], MagicMock())

    agent = MagicMock()
    agent.domain = "software-architect"
    agent.run = AsyncMock(return_value=_output("software-architect"))

    approvals = 0

    async def on_checkpoint(cp) -> None:
        nonlocal approvals
        cp.approved = True
        approvals += 1

    with patch.object(supervisor, "_build_agents", return_value=[agent]):
        package = await supervisor.run(
            "https://github.com/test/repo",
            "due_diligence",
            hitl_mode=HITLMode.SUPERVISED,
            on_checkpoint=on_checkpoint,
        )

    assert approvals == 3
    assert package.findings


@pytest.mark.asyncio
async def test_veto_callback_stops_run_before_package() -> None:
    llm = MagicMock()
    llm.complete = AsyncMock(return_value="Summary")
    supervisor = Supervisor(llm, [MagicMock()], MagicMock())

    agent = MagicMock()
    agent.domain = "software-architect"
    agent.run = AsyncMock(return_value=_output("software-architect"))

    async def on_checkpoint(cp) -> None:
        if cp.type == CheckpointType.FINDINGS_READY:
            raise RuntimeError("veto")

    with patch.object(supervisor, "_build_agents", return_value=[agent]):
        with pytest.raises(RuntimeError, match="veto"):
            await supervisor.run(
                "https://github.com/test/repo",
                "due_diligence",
                hitl_mode=HITLMode.SUPERVISED,
                on_checkpoint=on_checkpoint,
            )


@pytest.mark.asyncio
async def test_autopilot_mode_fires_no_checkpoints() -> None:
    llm = MagicMock()
    llm.complete = AsyncMock(return_value="Summary")
    supervisor = Supervisor(llm, [MagicMock()], MagicMock())

    agent = MagicMock()
    agent.domain = "software-architect"
    agent.run = AsyncMock(return_value=_output("software-architect"))

    called = False

    async def on_checkpoint(cp) -> None:
        nonlocal called
        called = True

    with patch.object(supervisor, "_build_agents", return_value=[agent]):
        await supervisor.run(
            "https://github.com/test/repo",
            "review",
            hitl_mode=HITLMode.AUTOPILOT,
            on_checkpoint=on_checkpoint,
        )

    assert called is False
