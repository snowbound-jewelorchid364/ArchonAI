from __future__ import annotations

from archon.engine.modes.vendor_evaluator import VendorInput, build_vendor_focus
from archon.output.sections.vendor_evaluator import render_vendor_evaluator
from archon.core.models import Finding, ReviewPackage, Severity


def _pkg() -> ReviewPackage:
    findings = [
        Finding(id="1", title="VendorA", description="desc", severity=Severity.HIGH, domain="cloud", recommendation="choose A", confidence=0.8),
        Finding(id="2", title="VendorB", description="desc", severity=Severity.MEDIUM, domain="data", recommendation="avoid lock-in", confidence=0.8),
    ]
    return ReviewPackage(
        run_id="r1",
        repo_url="https://github.com/o/r",
        mode="vendor_evaluator",
        duration_seconds=3.0,
        executive_summary="Vendor recommendation",
        findings=findings,
        artifacts=[],
        citations=[],
        agent_statuses={},
        partial=False,
        model_version="test",
    )


def test_default_criteria_applied_when_none_provided() -> None:
    data = VendorInput(use_case="object store", vendors=["A", "B"], evaluation_criteria=[])
    assert len(data.criteria) == 6
    assert "performance" in data.criteria


def test_build_vendor_focus_includes_all_vendors() -> None:
    focus = build_vendor_focus(VendorInput(use_case="db", vendors=["A", "B", "C"]))
    assert "A, B, C" in focus


def test_render_vendor_evaluator_has_matrix() -> None:
    out = render_vendor_evaluator(_pkg())
    assert "### Evaluation Matrix" in out
    assert "| Vendor | Criteria scores | Total |" in out


def test_render_vendor_evaluator_has_tco() -> None:
    out = render_vendor_evaluator(_pkg())
    assert "### 3-Year TCO Comparison" in out
