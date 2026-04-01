from __future__ import annotations
import uuid
import pytest
from archon.health.scorer import compute_health_score, SEVERITY_PENALTY, DOMAINS
from archon.core.models.finding import Finding, Severity
from archon.core.models.review_package import ReviewPackage


def _make_package(findings=None, repo_url="https://github.com/test/repo"):
    return ReviewPackage(
        run_id=str(uuid.uuid4()),
        repo_url=repo_url,
        mode="review",
        findings=findings or [],
        duration_seconds=1.0,
        executive_summary="",
    )


def _finding(domain: str, severity: Severity) -> Finding:
    return Finding(
        id=str(uuid.uuid4()),
        title="Test",
        description="desc",
        severity=severity,
        domain=domain,
        recommendation="fix it",
        confidence=0.9,
    )


def test_perfect_score_no_findings():
    pkg = _make_package()
    scores = compute_health_score(pkg)
    assert scores["overall"] == 100.0
    for d in DOMAINS:
        assert scores[d] == 100.0


def test_critical_finding_reduces_score():
    pkg = _make_package([_finding("security", Severity.CRITICAL)])
    scores = compute_health_score(pkg)
    expected = max(0.0, 100.0 - SEVERITY_PENALTY[Severity.CRITICAL])
    assert scores["security"] == expected


def test_score_floored_at_zero():
    findings = [_finding("software", Severity.CRITICAL)] * 10
    pkg = _make_package(findings)
    scores = compute_health_score(pkg)
    assert scores["software"] == 0.0


def test_domain_normalization_hyphen_style():
    pkg = _make_package([_finding("software-architect", Severity.HIGH)])
    scores = compute_health_score(pkg)
    expected = max(0.0, 100.0 - SEVERITY_PENALTY[Severity.HIGH])
    assert scores["software"] == expected


def test_weighted_overall():
    findings = [_finding("security", Severity.CRITICAL)] * 7
    pkg = _make_package(findings)
    scores = compute_health_score(pkg)
    assert scores["overall"] < 100.0
    assert scores["security"] == 0.0


def test_overall_rounded_to_one_decimal():
    pkg = _make_package([_finding("cloud", Severity.MEDIUM)])
    scores = compute_health_score(pkg)
    assert scores["overall"] == round(scores["overall"], 1)
