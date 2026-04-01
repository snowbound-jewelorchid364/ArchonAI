from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parents[2]))

from api.dependencies import require_user
from api.schemas.auth import CurrentUser
from api.routes.cost_optimiser import router as cost_router
from archon.core.models import Finding, ReviewPackage, Severity
from archon.engine.modes.cost_optimiser import CostOptimiserInput, build_cost_focus
from archon.input.cost_parser import CostParser
from archon.output.sections.cost_optimiser import render_cost_optimiser


def _pkg() -> ReviewPackage:
    findings = [
        Finding(id="1", title="EC2", description="desc", severity=Severity.HIGH, domain="cloud", recommendation="right-size", confidence=0.8),
        Finding(id="2", title="RDS", description="desc", severity=Severity.MEDIUM, domain="cloud", recommendation="reserved", confidence=0.8),
    ]
    return ReviewPackage(
        run_id="r1",
        repo_url="https://github.com/o/r",
        mode="cost_optimiser",
        duration_seconds=2.0,
        executive_summary="Summary",
        findings=findings,
        artifacts=[],
        citations=[],
        agent_statuses={},
        partial=False,
        model_version="test",
    )


def test_cost_parser_extracts_top_services() -> None:
    csv = "Service,MonthlyCost,PreviousMonthCost,Currency\nEC2,120,100,USD\nS3,30,40,USD\nRDS,80,80,USD\n"
    parsed = __import__("asyncio").run(CostParser().parse(csv))
    assert parsed.source_type == "cost_csv"
    assert parsed.metadata["total_monthly"] == 230.0
    assert parsed.metadata["top_services"][0]["service"] == "EC2"


def test_cost_parser_handles_empty_csv() -> None:
    parsed = __import__("asyncio").run(CostParser().parse(""))
    assert parsed.metadata["total_monthly"] == 0.0
    assert parsed.metadata["top_services"] == []


def test_build_cost_focus_includes_repo_url() -> None:
    focus = build_cost_focus(CostOptimiserInput(repo_url="https://github.com/o/r"))
    assert "https://github.com/o/r" in focus


def test_render_cost_optimiser_has_savings_table() -> None:
    out = render_cost_optimiser(_pkg())
    assert "### Top Savings Opportunities" in out
    assert "| Service | Current $/mo | Saving $/mo | Effort | Priority |" in out


@patch("api.routes.cost_optimiser.create_review", new_callable=AsyncMock)
@patch("api.routes.cost_optimiser.check_plan_limit", new_callable=AsyncMock)
def test_cost_optimiser_route_returns_job_id(mock_limit, mock_create) -> None:
    app = FastAPI()
    app.include_router(cost_router)

    async def _user():
        return CurrentUser(user_id="u1", email="u@x.com", plan="pro")

    app.dependency_overrides[require_user] = _user

    mock_limit.return_value = (True, "")
    mock_create.return_value = ("rev-1", "job-1")

    client = TestClient(app)
    resp = client.post(
        "/cost-optimiser/analyse",
        data={"repo_url": "https://github.com/o/r"},
        files={"cost_csv": ("cost.csv", "Service,MonthlyCost\nEC2,10", "text/csv")},
    )
    assert resp.status_code == 202
    assert resp.json()["job_id"] == "job-1"
