from __future__ import annotations

from archon.core.models import Finding, ReviewPackage, Severity
from archon.engine.modes.sunset_planner import SunsetInput, build_sunset_focus
from archon.output.sections.sunset_planner import render_sunset_planner


def _pkg() -> ReviewPackage:
    findings = [
        Finding(id="1", title="Legacy service", description="to remove", severity=Severity.HIGH, domain="integration", recommendation="drain traffic", confidence=0.8),
    ]
    return ReviewPackage(
        run_id="r1",
        repo_url="https://github.com/o/r",
        mode="sunset_planner",
        duration_seconds=2.0,
        executive_summary="sunset",
        findings=findings,
        artifacts=[],
        citations=[],
        agent_statuses={},
        partial=False,
        model_version="test",
    )


def test_build_sunset_focus_includes_service_name() -> None:
    focus = build_sunset_focus(SunsetInput(repo_url="https://github.com/o/r", service_to_sunset="legacy-api"))
    assert "legacy-api" in focus


def test_render_sunset_has_dependency_map() -> None:
    out = render_sunset_planner(_pkg())
    assert "### Dependency Map" in out


def test_render_sunset_has_shutdown_sequence() -> None:
    out = render_sunset_planner(_pkg())
    assert "### Shutdown Sequence" in out


def test_render_sunset_has_gdpr_checklist() -> None:
    out = render_sunset_planner(_pkg())
    assert "### GDPR Deletion Checklist" in out
