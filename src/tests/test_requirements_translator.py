"""Tests for Phase 7 requirements_translator."""
from __future__ import annotations
import json
import pytest
from unittest.mock import AsyncMock, MagicMock
from archon.engine.intake import ProductBrief
from archon.engine.requirements_translator import TechnicalConstraints, translate

BRIEF = ProductBrief(
    idea="A telemedicine platform for rural patients",
    users="Rural patients and doctors",
    core_value="Video consultations without reliable internet",
    scale_y1="1000 patients",
    scale_y2="10000 patients",
    budget_monthly="$500/month",
    timeline="6 months",
    compliance="HIPAA — we handle patient health records",
    raw_answers={},
)

VALID_LLM_RESPONSE = json.dumps({
    "user_type": "B2C",
    "estimated_rps": 5,
    "budget_monthly_usd": 500,
    "timeline_weeks": 26,
    "compliance_requirements": ["HIPAA"],
    "team_size_hint": "small",
    "suggested_options": ["lean", "scalable", "enterprise"],
})


@pytest.mark.asyncio
async def test_translate_returns_constraints():
    mock_llm = MagicMock()
    mock_llm.complete = AsyncMock(return_value=VALID_LLM_RESPONSE)
    result = await translate(BRIEF, mock_llm)
    assert isinstance(result, TechnicalConstraints)
    assert result.user_type == "B2C"
    assert result.budget_monthly_usd == 500
    assert result.timeline_weeks == 26


@pytest.mark.asyncio
async def test_translate_fallback_on_bad_json():
    mock_llm = MagicMock()
    mock_llm.complete = AsyncMock(return_value="not valid json at all")
    result = await translate(BRIEF, mock_llm)
    assert isinstance(result, TechnicalConstraints)
    # Should not raise, should return defaults
    assert result.suggested_options == ["lean", "scalable", "enterprise"]


@pytest.mark.asyncio
async def test_translate_detects_compliance():
    mock_llm = MagicMock()
    mock_llm.complete = AsyncMock(return_value=VALID_LLM_RESPONSE)
    result = await translate(BRIEF, mock_llm)
    assert "HIPAA" in result.compliance_requirements
