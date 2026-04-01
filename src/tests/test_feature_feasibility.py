from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from archon.engine.modes.feature_feasibility import FeatureInput, build_feature_focus
from archon.engine.modes.configs import get_mode
from archon.output.sections.feature_feasibility import render_feature_feasibility
from archon.core.models import Finding, ReviewPackage, Severity
from archon.engine.supervisor import Supervisor


def _pkg() -> ReviewPackage:
    findings = [
        Finding(id="1", title="risk-one", description="desc", severity=Severity.HIGH, domain="software", recommendation="fix", confidence=0.8),
        Finding(id="2", title="risk-two", description="desc", severity=Severity.MEDIUM, domain="cloud", recommendation="fix", confidence=0.8),
    ]
    return ReviewPackage(
        run_id="r1",
        repo_url="https://github.com/o/r",
        mode="feature_feasibility",
        duration_seconds=2.0,
        executive_summary="Feasible with prerequisites",
        findings=findings,
        artifacts=[],
        citations=[],
        agent_statuses={},
        partial=False,
        model_version="test",
    )


def test_build_feature_focus_contains_brief() -> None:
    focus = build_feature_focus(FeatureInput(repo_url="https://github.com/o/r", feature_brief="multi-region failover", deadline_weeks=6))
    assert "multi-region failover" in focus


def test_render_feasibility_has_verdict_section() -> None:
    out = render_feature_feasibility(_pkg())
    assert "### Verdict" in out


def test_render_feasibility_has_risk_register() -> None:
    out = render_feature_feasibility(_pkg())
    assert "### Risk Register" in out
    assert "| Risk | Likelihood | Impact | Mitigation |" in out


@pytest.mark.asyncio
async def test_feature_feasibility_runs_all_agents(mock_llm, mock_searcher) -> None:
    retriever = MagicMock()
    retriever.retrieve_as_context = AsyncMock(return_value="ctx")
    retriever.query = AsyncMock(return_value=[])
    supervisor = Supervisor(mock_llm, [mock_searcher], retriever)

    cfg = get_mode("feature_feasibility")
    agents = supervisor._build_agents(cfg)
    assert len(agents) == 6
