from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from archon.engine.modes.pr_reviewer import PRReviewInput, build_pr_focus
from archon.engine.supervisor import Supervisor
from archon.output.sections.pr_reviewer import render_pr_github_comment, render_pr_review
from archon.core.models import Finding, ReviewPackage, Severity


def _pkg(findings: list[Finding]) -> ReviewPackage:
    return ReviewPackage(
        run_id="r1",
        repo_url="https://github.com/o/r",
        mode="pr_reviewer",
        duration_seconds=1.0,
        executive_summary="PR summary",
        findings=findings,
        artifacts=[],
        citations=[],
        agent_statuses={},
        partial=False,
        model_version="test",
    )


def test_build_pr_focus_contains_blocker_categories() -> None:
    focus = build_pr_focus(
        PRReviewInput(
            pr_diff="diff --git a/a.py b/a.py",
            pr_title="Refactor auth",
            pr_description="Improve login",
            repo_url="https://github.com/o/r",
        )
    )
    assert "BLOCKER" in focus
    assert "WARNING" in focus
    assert "SUGGESTION" in focus


def test_render_pr_review_has_three_sections() -> None:
    findings = [
        Finding(id="1", title="A", description="d", severity=Severity.CRITICAL, domain="software", recommendation="fix", confidence=0.9),
        Finding(id="2", title="B", description="d", severity=Severity.HIGH, domain="software", recommendation="fix", confidence=0.9),
        Finding(id="3", title="C", description="d", severity=Severity.LOW, domain="software", recommendation="fix", confidence=0.9),
    ]
    out = render_pr_review(_pkg(findings))
    assert "### 🚫 Blockers" in out
    assert "### ⚠️ Warnings" in out
    assert "### 💡 Suggestions" in out


def test_render_pr_github_comment_is_valid_markdown() -> None:
    findings = [
        Finding(id="1", title="A", description="d", severity=Severity.HIGH, domain="software", recommendation="fix", confidence=0.9)
    ]
    out = render_pr_github_comment(_pkg(findings))
    assert out.startswith("## ARCHON PR Review")
    assert "**Verdict:**" in out


@pytest.mark.asyncio
async def test_pr_reviewer_only_uses_software_agent(mock_llm, mock_searcher) -> None:
    retriever = MagicMock()
    retriever.retrieve_as_context = AsyncMock(return_value="ctx")
    retriever.query = AsyncMock(return_value=[])
    supervisor = Supervisor(mock_llm, [mock_searcher], retriever)

    from archon.engine.modes.configs import get_mode

    agents = supervisor._build_agents(get_mode("pr_reviewer"))
    assert len(agents) == 1
    assert type(agents[0]).__name__ == "SoftwareArchitectAgent"


@pytest.mark.asyncio
async def test_pr_reviewer_times_out_at_90s(mock_llm, mock_searcher) -> None:
    retriever = MagicMock()
    retriever.retrieve_as_context = AsyncMock(return_value="ctx")
    retriever.query = AsyncMock(return_value=[])
    mock_llm.complete = AsyncMock(return_value="summary")

    supervisor = Supervisor(mock_llm, [mock_searcher], retriever)

    slow_agent = MagicMock()
    slow_agent.domain = "software-architect"
    slow_agent.run = AsyncMock(side_effect=asyncio.TimeoutError())

    with patch.object(supervisor, "_build_agents", return_value=[slow_agent]):
        package = await supervisor.run("https://github.com/o/r", "pr_reviewer")

    assert package.partial is True
    assert package.agent_statuses["software-architect"] in {"FAILED", "PARTIAL"}

