import pytest
from archon.config.settings import Settings
from archon.engine.modes.configs import ALL_MODES, get_mode, ModeConfig


class TestSettingsThinkingBudget:
    def test_default_mode_returns_medium(self):
        s = Settings(anthropic_api_key="test")
        assert s.thinking_budget_for_mode("review") == "medium"

    def test_premium_mode_returns_high(self):
        s = Settings(anthropic_api_key="test")
        assert s.thinking_budget_for_mode("due_diligence") == "high"
        assert s.thinking_budget_for_mode("compliance_auditor") == "high"

    def test_fast_mode_returns_low(self):
        s = Settings(anthropic_api_key="test")
        assert s.thinking_budget_for_mode("drift_monitor") == "low"

    def test_unknown_mode_returns_default(self):
        s = Settings(anthropic_api_key="test")
        assert s.thinking_budget_for_mode("unknown_mode") == "medium"


class TestSettingsRequireKeys:
    def test_require_missing_key_raises(self):
        s = Settings()
        with pytest.raises(ValueError, match="Missing required config"):
            s.require_keys("anthropic_api_key")

    def test_require_present_key_passes(self):
        s = Settings(anthropic_api_key="sk-test-123")
        s.require_keys("anthropic_api_key")


class TestAllModes:
    def test_14_modes_registered(self):
        assert len(ALL_MODES) == 15

    def test_all_mode_names(self):
        expected = {
            "review", "design", "migration_planner", "compliance_auditor",
            "due_diligence", "incident_responder", "cost_optimiser",
            "pr_reviewer", "scaling_advisor", "drift_monitor",
            "feature_feasibility", "vendor_evaluator",
            "onboarding_accelerator", "sunset_planner",
            "idea_mode"
        }
        assert set(ALL_MODES.keys()) == expected

    def test_each_mode_has_active_agents(self):
        for name, cfg in ALL_MODES.items():
            assert len(cfg.active_agents) >= 1, f"{name} has no agents"

    def test_get_mode_valid(self):
        cfg = get_mode("review")
        assert isinstance(cfg, ModeConfig)
        assert cfg.name == "review"

    def test_get_mode_invalid_raises(self):
        with pytest.raises(ValueError):
            get_mode("nonexistent_mode")

    def test_mode_agents_are_valid_keys(self):
        valid_agents = {"software", "cloud", "security", "data", "integration", "ai"}
        for name, cfg in ALL_MODES.items():
            for agent in cfg.active_agents:
                assert agent in valid_agents, f"{name} has invalid agent {agent}"
