"""Tests for Supervisor orchestrator."""
from __future__ import annotations
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from archon.engine.supervisor import Supervisor, AGENT_REGISTRY
from archon.core.models.agent_output import AgentOutput
from archon.core.models.finding import Finding, Severity
from archon.core.models.review_package import ReviewPackage
from archon.engine.modes.configs import get_mode


def _make_output(domain, findings=None, error=None):
    return AgentOutput(
        domain=domain,
        findings=findings or [],
        confidence=0.8 if not error else 0.0,
        duration_seconds=5.0,
        error=error,
        partial=bool(error),
    )


class TestSupervisor:
    @pytest.mark.asyncio
    async def test_run_returns_review_package(self, mock_llm, mock_searcher):
        mock_llm.complete = AsyncMock(return_value="Executive summary here.")
        retriever = MagicMock()
        retriever.retrieve_as_context = AsyncMock(return_value="context")
        retriever.query = AsyncMock(return_value=[])
        supervisor = Supervisor(mock_llm, [mock_searcher], retriever)

        # Patch _build_agents so we control what runs
        fake_agent = MagicMock()
        fake_agent.domain = "software-architect"
        fake_agent.run = AsyncMock(return_value=_make_output("software-architect"))
        with patch.object(supervisor, "_build_agents", return_value=[fake_agent]):
            package = await supervisor.run("https://github.com/test/repo", "review")

        assert isinstance(package, ReviewPackage)
        assert package.mode == "review"
        assert "software-architect" in package.agent_statuses

    @pytest.mark.asyncio
    async def test_mode_aware_agent_routing(self, mock_llm, mock_searcher):
        retriever = MagicMock()
        retriever.retrieve_as_context = AsyncMock(return_value="ctx")
        retriever.query = AsyncMock(return_value=[])
        supervisor = Supervisor(mock_llm, [mock_searcher], retriever)

        mode_cfg = get_mode("incident_responder")
        agents = supervisor._build_agents(mode_cfg)
        agent_domains = {type(a).__name__ for a in agents}
        # incident_responder uses only software + cloud
        assert len(agents) == 2
        assert "SoftwareArchitectAgent" in agent_domains
        assert "CloudArchitectAgent" in agent_domains

    @pytest.mark.asyncio
    async def test_all_14_modes_build_agents(self, mock_llm, mock_searcher):
        retriever = MagicMock()
        retriever.retrieve_as_context = AsyncMock(return_value="ctx")
        retriever.query = AsyncMock(return_value=[])
        supervisor = Supervisor(mock_llm, [mock_searcher], retriever)

        from archon.engine.modes.configs import ALL_MODES
        for mode_name, cfg in ALL_MODES.items():
            agents = supervisor._build_agents(cfg)
            assert len(agents) == len(cfg.active_agents), f"Mode {mode_name} agent count mismatch"

    @pytest.mark.asyncio
    async def test_deduplication(self, mock_llm, mock_searcher):
        retriever = MagicMock()
        retriever.retrieve_as_context = AsyncMock(return_value="ctx")
        supervisor = Supervisor(mock_llm, [mock_searcher], retriever)

        f1 = Finding(id="1", title="Same Issue", description="d", severity=Severity.HIGH,
                     domain="security", recommendation="r", confidence=0.8)
        f2 = Finding(id="2", title="Same Issue", description="d2", severity=Severity.HIGH,
                     domain="cloud", recommendation="r2", confidence=0.7)

        deduped = supervisor._deduplicate([f1, f2])
        assert len(deduped) == 1

    @pytest.mark.asyncio
    async def test_dedup_keeps_different(self, mock_llm, mock_searcher):
        retriever = MagicMock()
        retriever.retrieve_as_context = AsyncMock(return_value="ctx")
        supervisor = Supervisor(mock_llm, [mock_searcher], retriever)

        f1 = Finding(id="1", title="Issue A", description="d", severity=Severity.HIGH,
                     domain="security", recommendation="r", confidence=0.8)
        f2 = Finding(id="2", title="Issue B", description="d2", severity=Severity.MEDIUM,
                     domain="cloud", recommendation="r2", confidence=0.7)

        deduped = supervisor._deduplicate([f1, f2])
        assert len(deduped) == 2

    @pytest.mark.asyncio
    async def test_agent_exception_handled(self, mock_llm, mock_searcher):
        mock_llm.complete = AsyncMock(return_value="Summary")
        retriever = MagicMock()
        retriever.retrieve_as_context = AsyncMock(return_value="ctx")
        retriever.query = AsyncMock(return_value=[])
        supervisor = Supervisor(mock_llm, [mock_searcher], retriever)

        ok_agent = MagicMock()
        ok_agent.domain = "cloud-architect"
        ok_agent.run = AsyncMock(return_value=_make_output("cloud-architect"))

        bad_agent = MagicMock()
        bad_agent.domain = "software-architect"
        bad_agent.run = AsyncMock(side_effect=RuntimeError("boom"))

        with patch.object(supervisor, "_build_agents", return_value=[bad_agent, ok_agent]):
            package = await supervisor.run("https://github.com/test/repo", "review")

        assert package.partial is True
        assert package.agent_statuses["software-architect"] == "FAILED"
        assert package.agent_statuses["cloud-architect"] == "COMPLETED"

    @pytest.mark.asyncio
    async def test_hitl_override_incident(self, mock_llm, mock_searcher):
        retriever = MagicMock()
        supervisor = Supervisor(mock_llm, [mock_searcher], retriever)
        from archon.engine.hitl.checkpoints import HITLMode

        # Incident always gets autopilot regardless of request
        resolved = supervisor._resolve_hitl("incident_responder", HITLMode.SUPERVISED)
        assert resolved == HITLMode.AUTOPILOT

    @pytest.mark.asyncio
    async def test_hitl_minimum_due_diligence(self, mock_llm, mock_searcher):
        retriever = MagicMock()
        supervisor = Supervisor(mock_llm, [mock_searcher], retriever)
        from archon.engine.hitl.checkpoints import HITLMode

        # Due diligence forces minimum SUPERVISED
        resolved = supervisor._resolve_hitl("due_diligence", HITLMode.AUTOPILOT)
        assert resolved == HITLMode.SUPERVISED
