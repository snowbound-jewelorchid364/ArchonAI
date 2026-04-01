from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from archon.core.models import AgentOutput, Artifact, ArtifactType, Finding, Severity
from archon.engine.supervisor import Supervisor


def _finding(domain: str) -> Finding:
    return Finding(
        id=str(uuid.uuid4()),
        title=f"{domain} design finding",
        description="desc",
        severity=Severity.MEDIUM,
        domain=domain,
        recommendation="fix",
        confidence=0.8,
    )


def _artifact_set() -> list[Artifact]:
    return [
        Artifact(
            id=str(uuid.uuid4()),
            artifact_type=ArtifactType.ADR,
            title="ADR-001",
            content="## Decision\nUse FastAPI",
            filename="adr-001.md",
        ),
        Artifact(
            id=str(uuid.uuid4()),
            artifact_type=ArtifactType.ADR,
            title="ADR-002",
            content="## Decision\nUse PostgreSQL",
            filename="adr-002.md",
        ),
        Artifact(
            id=str(uuid.uuid4()),
            artifact_type=ArtifactType.ADR,
            title="ADR-003",
            content="## Decision\nUse Redis",
            filename="adr-003.md",
        ),
        Artifact(
            id=str(uuid.uuid4()),
            artifact_type=ArtifactType.DIAGRAM,
            title="Container Diagram",
            content="graph TD; API-->DB",
            filename="container.mmd",
        ),
    ]


@pytest.mark.asyncio
async def test_e2e_design_pipeline_brief_produces_adrs_and_diagram() -> None:
    llm = AsyncMock()
    llm.complete = AsyncMock(return_value="Design summary")
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
        artifacts = _artifact_set() if i == 0 else []
        a.run = AsyncMock(
            return_value=AgentOutput(
                domain=d,
                findings=[_finding(d)],
                artifacts=artifacts,
                confidence=0.9,
                duration_seconds=0.2,
            )
        )
        agents.append(a)

    with patch.object(supervisor, "_build_agents", return_value=agents):
        package = await supervisor.run(
            "B2B SaaS, REST API, PostgreSQL, 10k users",
            "design",
        )

    stack_recommendation = ", ".join(a.title for a in package.artifacts if a.artifact_type == ArtifactType.ADR)
    assert stack_recommendation

    adrs = [a for a in package.artifacts if a.artifact_type == ArtifactType.ADR]
    diagrams = [a for a in package.artifacts if a.artifact_type == ArtifactType.DIAGRAM]

    assert len(adrs) >= 3
    assert len(diagrams) >= 1
