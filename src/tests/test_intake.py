"""Tests for Phase 7 Intake engine."""
from __future__ import annotations
import pytest
from archon.engine.intake import (
    INTAKE_QUESTIONS,
    ProductBrief,
    run_intake,
)

ALL_ANSWERS = {
    "users": "Small business owners",
    "core_value": "One-click invoice generation",
    "scale": "500 in year 1, 5000 in year 2",
    "budget": "$200 per month",
    "timeline": "3 months",
    "compliance": "None",
}


@pytest.mark.asyncio
async def test_intake_all_questions_answered():
    brief = await run_intake("Invoicing SaaS", ALL_ANSWERS)
    assert isinstance(brief, ProductBrief)
    assert brief.idea == "Invoicing SaaS"
    assert "Small business" in brief.users
    assert brief.budget_monthly == "$200 per month"
    assert brief.timeline == "3 months"


@pytest.mark.asyncio
async def test_intake_missing_answer_raises():
    partial = {k: v for k, v in ALL_ANSWERS.items() if k != "budget"}
    with pytest.raises(ValueError, match="Missing answers"):
        await run_intake("Invoicing SaaS", partial)


def test_intake_questions_are_plain_english():
    technical_terms = {"RPS", "latency", "throughput", "SLA", "API endpoint", "p99", "IOPS"}
    for _key, question in INTAKE_QUESTIONS:
        for term in technical_terms:
            assert term.lower() not in question.lower(), (
                f"Question contains technical term '{term}': {question}"
            )
