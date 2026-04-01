"""Tests for core Pydantic models."""
from __future__ import annotations
import pytest
from archon.core.models.finding import Finding, Severity, Citation
from archon.core.models.agent_output import AgentOutput
from archon.core.models.artifact import Artifact, ArtifactType
from archon.core.models.review_package import ReviewPackage


class TestSeverity:
    def test_enum_values(self):
        assert Severity.CRITICAL.value == "CRITICAL"
        assert Severity.HIGH.value == "HIGH"
        assert Severity.MEDIUM.value == "MEDIUM"
        assert Severity.LOW.value == "LOW"
        assert Severity.INFO.value == "INFO"

    def test_all_values_present(self):
        assert len(Severity) == 5


class TestCitation:
    def test_valid_citation(self, sample_citation):
        assert sample_citation.credibility_score == 0.95
        assert "OWASP" in sample_citation.title

    def test_default_credibility(self):
        c = Citation(url="https://example.com", title="Test", excerpt="x")
        assert c.credibility_score == 0.5

    def test_excerpt_max_length(self):
        with pytest.raises(Exception):
            Citation(url="https://example.com", title="T", excerpt="x" * 301)

    def test_credibility_bounds(self):
        with pytest.raises(Exception):
            Citation(url="https://example.com", title="T", excerpt="x", credibility_score=1.5)
        with pytest.raises(Exception):
            Citation(url="https://example.com", title="T", excerpt="x", credibility_score=-0.1)


class TestFinding:
    def test_valid_finding(self, sample_finding):
        assert sample_finding.severity == Severity.CRITICAL
        assert sample_finding.from_codebase is True
        assert sample_finding.confidence == 0.95

    def test_optional_fields_default_none(self):
        f = Finding(id="x", title="t", description="d", severity=Severity.LOW,
                    domain="test", recommendation="r", confidence=0.5)
        assert f.file_path is None
        assert f.line_number is None
        assert f.citations == []

    def test_confidence_bounds(self):
        with pytest.raises(Exception):
            Finding(id="x", title="t", description="d", severity=Severity.LOW,
                    domain="test", recommendation="r", confidence=1.5)


class TestArtifact:
    def test_valid_artifact(self, sample_artifact):
        assert sample_artifact.artifact_type == ArtifactType.ADR
        assert sample_artifact.filename == "adr-001.md"

    def test_artifact_types(self):
        assert len(ArtifactType) == 4
        for t in ["ADR", "TERRAFORM", "DIAGRAM", "RUNBOOK"]:
            assert ArtifactType(t)


class TestAgentOutput:
    def test_agent_output(self, sample_agent_output):
        assert sample_agent_output.domain == "security"
        assert sample_agent_output.confidence == 0.85
        assert len(sample_agent_output.findings) == 1

    def test_defaults(self):
        ao = AgentOutput(domain="test", confidence=0.5, duration_seconds=1.0)
        assert ao.findings == []
        assert ao.citations == []
        assert ao.artifacts == []
        assert ao.error is None
        assert ao.partial is False

    def test_error_output(self):
        ao = AgentOutput(domain="test", confidence=0.0, duration_seconds=0.0,
                         error="timed out", partial=True)
        assert ao.error == "timed out"
        assert ao.partial is True


class TestReviewPackage:
    def test_severity_counts(self, sample_package):
        counts = sample_package.severity_counts
        assert counts["CRITICAL"] == 1
        assert counts["HIGH"] == 2
        assert counts["MEDIUM"] == 2
        assert counts["LOW"] == 1

    def test_critical_findings(self, sample_package):
        crits = sample_package.critical_findings
        assert len(crits) == 1
        assert crits[0].severity == Severity.CRITICAL

    def test_high_findings(self, sample_package):
        highs = sample_package.high_findings
        assert len(highs) == 2

    def test_all_findings(self, sample_package):
        assert len(sample_package.all_findings()) == 6

    def test_partial_flag(self, partial_package):
        assert partial_package.partial is True
        assert len(partial_package.findings) == 3
