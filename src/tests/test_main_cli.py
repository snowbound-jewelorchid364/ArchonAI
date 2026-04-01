"""Tests for CLI argument parsing and main entry point."""
from __future__ import annotations
import pytest
from unittest.mock import patch, AsyncMock
import argparse


class TestCLIParsing:
    def test_all_modes_list(self):
        # Import the ALL_MODES from main
        import importlib.util
        spec = importlib.util.spec_from_file_location("main", "main.py")
        main_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_mod)
        assert "review" in main_mod.ALL_MODES
        assert "design" in main_mod.ALL_MODES
        assert len(main_mod.ALL_MODES) == 14

    def test_14_modes_present(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("main", "main.py")
        main_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_mod)
        expected = [
            "review", "design", "migration_planner", "compliance_auditor",
            "due_diligence", "incident_responder", "cost_optimiser", "pr_reviewer",
            "scaling_advisor", "drift_monitor", "feature_feasibility",
            "vendor_evaluator", "onboarding_accelerator", "sunset_planner",
        ]
        for mode in expected:
            assert mode in main_mod.ALL_MODES

    def test_parser_creation(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("main", "main.py")
        main_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_mod)
        # main() creates the parser; we just verify the module loads
        assert hasattr(main_mod, "main")
        assert hasattr(main_mod, "run")
