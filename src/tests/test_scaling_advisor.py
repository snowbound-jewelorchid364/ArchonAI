from __future__ import annotations

import asyncio

from archon.core.models import Finding, ReviewPackage, Severity
from archon.engine.modes.scaling_advisor import ScalingInput, build_scaling_focus
from archon.input.apm_parser import APMParser
from archon.output.sections.scaling_advisor import render_scaling_advisor


def _pkg() -> ReviewPackage:
    findings = [
        Finding(id="1", title="api-service", description="cpu saturation", severity=Severity.HIGH, domain="cloud", recommendation="scale out", confidence=0.8),
        Finding(id="2", title="db", description="connection limits", severity=Severity.CRITICAL, domain="data", recommendation="pooling", confidence=0.8),
    ]
    return ReviewPackage(
        run_id="r1",
        repo_url="https://github.com/o/r",
        mode="scaling_advisor",
        duration_seconds=4.0,
        executive_summary="Scale findings",
        findings=findings,
        artifacts=[],
        citations=[],
        agent_statuses={},
        partial=False,
        model_version="test",
    )


def test_apm_parser_extracts_p99_latency() -> None:
    payload = {
        "endpoints": [
            {"endpoint": "/v1/a", "p50": 10, "p95": 50, "p99": 100, "error_rate_pct": 1.2, "rps": 40},
            {"endpoint": "/v1/b", "p50": 20, "p95": 60, "p99": 240, "error_rate_pct": 0.4, "rps": 30},
        ]
    }
    parsed = asyncio.run(APMParser().parse(__import__("json").dumps(payload)))
    assert parsed.metadata["p99_latency_ms"] == 240.0


def test_build_scaling_focus_includes_rps_values() -> None:
    focus = build_scaling_focus(ScalingInput(repo_url="https://github.com/o/r", current_rps=100, target_rps=1200))
    assert "1200" in focus
    assert "100" in focus


def test_render_scaling_advisor_has_bottleneck_table() -> None:
    out = render_scaling_advisor(_pkg())
    assert "### Bottleneck Ranking" in out
    assert "| Component | Failure Mode | Breaking Point RPS | Fix |" in out


def test_render_scaling_advisor_has_cost_model() -> None:
    out = render_scaling_advisor(_pkg())
    assert "### Cost Model at Scale" in out
