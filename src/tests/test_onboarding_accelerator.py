from __future__ import annotations

from archon.core.models import Finding, ReviewPackage, Severity
from archon.engine.modes.onboarding_accelerator import OnboardingInput, build_onboarding_focus
from archon.output.sections.onboarding_accelerator import render_onboarding_accelerator


def _pkg() -> ReviewPackage:
    findings = [
        Finding(id="1", title="Auth flow", description="complex path", severity=Severity.HIGH, domain="software", recommendation="doc flow", confidence=0.8),
    ]
    return ReviewPackage(
        run_id="r1",
        repo_url="https://github.com/o/r",
        mode="onboarding_accelerator",
        duration_seconds=2.0,
        executive_summary="onboarding",
        findings=findings,
        artifacts=[],
        citations=[],
        agent_statuses={},
        partial=False,
        model_version="test",
    )


def test_build_onboarding_focus_includes_role() -> None:
    focus = build_onboarding_focus(OnboardingInput(repo_url="https://github.com/o/r", role="staff engineer"))
    assert "staff engineer" in focus


def test_render_onboarding_has_system_map() -> None:
    out = render_onboarding_accelerator(_pkg())
    assert "### System Map" in out


def test_render_onboarding_has_first_week() -> None:
    out = render_onboarding_accelerator(_pkg())
    assert "### First Week" in out


def test_render_onboarding_has_landmines() -> None:
    out = render_onboarding_accelerator(_pkg())
    assert "### Known Landmines" in out
