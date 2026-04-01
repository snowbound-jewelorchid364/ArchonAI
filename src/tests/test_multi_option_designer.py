"""Tests for Phase 7 multi_option_designer."""
from __future__ import annotations
import json
import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock
from archon.core.models.review_package import ReviewPackage
from archon.engine.requirements_translator import TechnicalConstraints
from archon.engine.multi_option_designer import ArchitectureOption, generate_options

THREE_OPTIONS_JSON = '[{"id": "lean", "name": "Lean MVP", "tagline": "Get to market fast with minimal cost", "monthly_cost_estimate": "$150/month", "team_size": "1-2 engineers", "time_to_mvp": "6 weeks", "tech_stack": ["Next.js", "Supabase", "Vercel", "Stripe"], "key_tradeoffs": ["Fast to build", "Limited scalability"], "adrs": [], "suitable_for": "Early validation, solo founders"}, {"id": "scalable", "name": "Growth-Ready", "tagline": "Built to handle 10x traffic without rewrite", "monthly_cost_estimate": "$800/month", "team_size": "3-5 engineers", "time_to_mvp": "12 weeks", "tech_stack": ["React", "FastAPI", "PostgreSQL", "Redis", "AWS ECS"], "key_tradeoffs": ["More upfront work", "Scales to thousands of users"], "adrs": [], "suitable_for": "Post-seed, growing teams"}, {"id": "enterprise", "name": "Enterprise-Scale", "tagline": "Multi-region, SOC2-ready from day one", "monthly_cost_estimate": "$5000/month", "team_size": "8+ engineers", "time_to_mvp": "24 weeks", "tech_stack": ["React", "Go microservices", "PostgreSQL", "Kubernetes", "Datadog"], "key_tradeoffs": ["High complexity", "Future-proof for enterprise deals"], "adrs": ["ADR-001: Microservices over monolith"], "suitable_for": "Enterprises, regulated industries"}]'

def _make_package():
    return ReviewPackage(
        run_id="run-test-001",
        repo_url="idea:test",
        mode="idea_mode",
        created_at=datetime.now(UTC),
        duration_seconds=1.0,
        executive_summary="",
        findings=[],
        artifacts=[],
        citations=[],
        agent_statuses={},
        partial=False,
    )

def _make_constraints():
    return TechnicalConstraints(
        user_type="B2C",
        estimated_rps=10,
        budget_monthly_usd=300,
        timeline_weeks=12,
        compliance_requirements=[],
        team_size_hint="small",
        suggested_options=["lean", "scalable", "enterprise"],
    )


@pytest.mark.asyncio
async def test_generates_three_options():
    mock_llm = AsyncMock()
    mock_llm.complete = AsyncMock(return_value=THREE_OPTIONS_JSON)
    options = await generate_options(_make_package(), _make_constraints(), mock_llm)
    assert len(options) == 3
    assert all(isinstance(o, ArchitectureOption) for o in options)


@pytest.mark.asyncio
async def test_option_ids_correct():
    mock_llm = AsyncMock()
    mock_llm.complete = AsyncMock(return_value=THREE_OPTIONS_JSON)
    options = await generate_options(_make_package(), _make_constraints(), mock_llm)
    ids = {o.id for o in options}
    assert ids == {"lean", "scalable", "enterprise"}


@pytest.mark.asyncio
async def test_lean_cheaper_than_enterprise():
    mock_llm = AsyncMock()
    mock_llm.complete = AsyncMock(return_value=THREE_OPTIONS_JSON)
    options = await generate_options(_make_package(), _make_constraints(), mock_llm)
    by_id = {o.id: o for o in options}
    # Lean should be cheaper — verify enterprise cost contains bigger number
    assert "5000" in by_id["enterprise"].monthly_cost_estimate
    assert "150" in by_id["lean"].monthly_cost_estimate
