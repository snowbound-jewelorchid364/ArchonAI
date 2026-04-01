from __future__ import annotations

import uuid

import pytest

from archon.core.models import Artifact, ArtifactType, Finding, ReviewPackage, Severity
from archon.engine.modes.configs import ALL_MODES
from archon.output.formatter import MarkdownFormatter


def _base_package(mode: str) -> ReviewPackage:
    finding = Finding(
        id=str(uuid.uuid4()),
        title="Cost and compliance risk",
        description="A sample finding used across formatter mode tests.",
        severity=Severity.HIGH,
        domain="cloud-architect",
        recommendation="Apply remediation.",
        confidence=0.8,
    )
    artifacts = [
        Artifact(
            id=str(uuid.uuid4()),
            artifact_type=ArtifactType.ADR,
            title="ADR-001",
            content="## Decision\nUse PostgreSQL.",
            filename="adr-001.md",
        ),
        Artifact(
            id=str(uuid.uuid4()),
            artifact_type=ArtifactType.DIAGRAM,
            title="C4",
            content="graph TD; A-->B",
            filename="system.mmd",
        ),
        Artifact(
            id=str(uuid.uuid4()),
            artifact_type=ArtifactType.TERRAFORM,
            title="main.tf",
            content="resource \"azurerm_resource_group\" \"rg\" {}",
            filename="main.tf",
        ),
    ]
    return ReviewPackage(
        run_id=str(uuid.uuid4()),
        repo_url="https://github.com/test/repo",
        mode=mode,
        duration_seconds=1.0,
        executive_summary="Short executive summary.",
        findings=[finding],
        artifacts=artifacts,
        agent_statuses={"software-architect": "COMPLETED"},
    )


def test_formatter_all_modes_non_empty_and_no_exceptions() -> None:
    fmt = MarkdownFormatter()
    for mode in ALL_MODES:
        package = _base_package(mode)
        output = fmt.format(package)
        assert isinstance(output, str)
        assert output.strip()


def test_mode_specific_sections_present() -> None:
    fmt = MarkdownFormatter()

    review_md = fmt.format(_base_package("review"))
    design_md = fmt.format(_base_package("design"))
    compliance_md = fmt.format(_base_package("compliance_auditor"))
    cost_md = fmt.format(_base_package("cost_optimiser"))
    incident_md = fmt.format(_base_package("incident_responder"))

    assert "## Executive Summary" in review_md
    assert "## Executive Summary" in design_md
    assert "## Compliance Gaps" in compliance_md
    assert "## Savings Opportunities" in cost_md
    assert "## Immediate Actions" in incident_md
