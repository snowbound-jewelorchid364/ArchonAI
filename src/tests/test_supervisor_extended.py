import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from archon.engine.supervisor import Supervisor, AGENT_REGISTRY, MODE_HITL_OVERRIDES, MODE_HITL_MINIMUM
from archon.engine.modes.configs import get_mode, ALL_MODES
from archon.engine.hitl.checkpoints import HITLMode


def _make_supervisor():
    llm = MagicMock()
    searchers = [MagicMock()]
    retriever = MagicMock()
    return Supervisor(llm, searchers, retriever)


class TestSupervisorBuildAgents:
    def test_review_builds_all_6(self):
        sup = _make_supervisor()
        mode_config = get_mode("review")
        agents = sup._build_agents(mode_config)
        assert len(agents) == 6

    def test_incident_builds_2(self):
        sup = _make_supervisor()
        mode_config = get_mode("incident_responder")
        agents = sup._build_agents(mode_config)
        assert len(agents) == 2

    def test_pr_reviewer_builds_2(self):
        sup = _make_supervisor()
        mode_config = get_mode("pr_reviewer")
        agents = sup._build_agents(mode_config)
        assert len(agents) == 2

    def test_all_modes_build_agents(self):
        sup = _make_supervisor()
        for mode_name, mode_config in ALL_MODES.items():
            agents = sup._build_agents(mode_config)
            assert len(agents) >= 1, f"Mode {mode_name} built 0 agents"
            assert len(agents) == len(mode_config.active_agents)


class TestSupervisorHITL:
    def test_incident_forces_autopilot(self):
        sup = _make_supervisor()
        result = sup._resolve_hitl("incident_responder", HITLMode.SUPERVISED)
        assert result == HITLMode.AUTOPILOT

    def test_due_diligence_minimum_supervised(self):
        sup = _make_supervisor()
        result = sup._resolve_hitl("due_diligence", HITLMode.AUTOPILOT)
        assert result == HITLMode.SUPERVISED

    def test_compliance_minimum_balanced(self):
        sup = _make_supervisor()
        result = sup._resolve_hitl("compliance_auditor", HITLMode.AUTOPILOT)
        assert result == HITLMode.BALANCED

    def test_review_respects_user_choice(self):
        sup = _make_supervisor()
        result = sup._resolve_hitl("review", HITLMode.BALANCED)
        assert result == HITLMode.BALANCED

    def test_normal_mode_autopilot(self):
        sup = _make_supervisor()
        result = sup._resolve_hitl("design", HITLMode.AUTOPILOT)
        assert result == HITLMode.AUTOPILOT


class TestAgentRegistry:
    def test_all_6_agents_registered(self):
        assert len(AGENT_REGISTRY) == 6
        expected = {"software", "cloud", "security", "data", "integration", "ai"}
        assert set(AGENT_REGISTRY.keys()) == expected

    def test_all_agents_are_classes(self):
        for key, cls in AGENT_REGISTRY.items():
            assert callable(cls), f"{key} is not callable"
