"""Tests for ConfidenceScorer."""
from __future__ import annotations
import pytest
from archon.output.confidence import ConfidenceScorer
from archon.core.models.finding import Finding, Severity, Citation
from archon.core.models.agent_output import AgentOutput


class TestConfidenceScorer:
    def test_score_finding_basic(self, sample_finding):
        scorer = ConfidenceScorer()
        score = scorer.score_finding(sample_finding)
        assert 0.0 <= score <= 1.0

    def test_score_finding_no_citations(self):
        scorer = ConfidenceScorer()
        f = Finding(id="t1", title="T", description="D", severity=Severity.LOW,
                    domain="test", recommendation="R", confidence=0.8, from_codebase=True)
        score = scorer.score_finding(f)
        assert score == 0.8

    def test_score_finding_not_from_codebase(self):
        scorer = ConfidenceScorer()
        f = Finding(id="t2", title="T", description="D", severity=Severity.LOW,
                    domain="test", recommendation="R", confidence=1.0, from_codebase=False)
        score = scorer.score_finding(f)
        assert score < 1.0

    def test_score_finding_with_citations(self):
        scorer = ConfidenceScorer()
        c = Citation(url="https://example.com", title="E", excerpt="e", credibility_score=1.0)
        f = Finding(id="t3", title="T", description="D", severity=Severity.HIGH,
                    domain="test", recommendation="R", confidence=0.8,
                    from_codebase=True, citations=[c])
        score = scorer.score_finding(f)
        assert 0.0 <= score <= 1.0

    def test_score_agent(self, sample_agent_output):
        scorer = ConfidenceScorer()
        score = scorer.score_agent(sample_agent_output)
        assert 0.0 <= score <= 1.0

    def test_score_agent_empty(self):
        scorer = ConfidenceScorer()
        output = AgentOutput(domain="test", confidence=0.5, duration_seconds=1.0)
        assert scorer.score_agent(output) == 0.0

    def test_score_package(self, sample_package):
        scorer = ConfidenceScorer()
        score = scorer.score_package(sample_package)
        assert 0.0 <= score <= 1.0

    def test_grade_a(self):
        assert ConfidenceScorer().grade(0.95) == "A"

    def test_grade_b(self):
        assert ConfidenceScorer().grade(0.8) == "B"

    def test_grade_c(self):
        assert ConfidenceScorer().grade(0.65) == "C"

    def test_grade_d(self):
        assert ConfidenceScorer().grade(0.45) == "D"

    def test_grade_f(self):
        assert ConfidenceScorer().grade(0.2) == "F"