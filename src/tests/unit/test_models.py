from __future__ import annotations
import pytest
from pydantic import ValidationError
from archon.core.models.finding import Finding, Severity, Citation
from archon.core.models.agent_output import AgentOutput
from archon.core.models.review_package import ReviewPackage


def test_finding_requires_citation_for_critical(sample_finding):
    assert len(sample_finding.citations) >= 1
    assert sample_finding.severity == Severity.CRITICAL


def test_finding_confidence_range():
    with pytest.raises(ValidationError):
        Finding(
            id="x", title="t", description="d", severity=Severity.LOW,
            domain="software", recommendation="r", confidence=1.5, from_codebase=True,
        )


def test_agent_output_partial_on_error():
    out = AgentOutput(domain="cloud", confidence=0.0, duration_seconds=1.0, error="timeout", partial=True)
    assert out.partial is True
    assert out.error == "timeout"
    assert out.findings == []


def test_citation_excerpt_max_length():
    with pytest.raises(ValidationError):
        Citation(
            url="https://example.com",
            title="Test",
            excerpt="x" * 301,
            credibility_score=0.5,
        )
