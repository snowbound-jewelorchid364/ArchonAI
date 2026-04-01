"""Tests for config settings."""
from __future__ import annotations
import pytest
from archon.config.settings import Settings


class TestSettings:
    def test_defaults(self):
        s = Settings()
        assert s.agent_model == "claude-opus-4-5"
        assert s.fast_model == "claude-haiku-4-5"
        assert s.rag_chunk_size == 500
        assert s.rag_chunk_overlap == 50
        assert s.rag_top_k == 8
        assert s.max_loc == 500_000
        assert s.agent_timeout_seconds == 1200

    def test_thinking_budget_review(self):
        s = Settings()
        assert s.thinking_budget_for_mode("review") == "medium"

    def test_thinking_budget_premium(self):
        s = Settings()
        assert s.thinking_budget_for_mode("due_diligence") == "high"
        assert s.thinking_budget_for_mode("compliance_auditor") == "high"

    def test_thinking_budget_fast(self):
        s = Settings()
        assert s.thinking_budget_for_mode("drift_monitor") == "low"

    def test_require_keys_raises(self):
        s = Settings()
        with pytest.raises(ValueError, match="anthropic_api_key"):
            s.require_keys("anthropic_api_key")

    def test_require_keys_passes_with_values(self):
        s = Settings(anthropic_api_key="sk-test")
        s.require_keys("anthropic_api_key")
