"""Tests for agent JSON parser."""
from __future__ import annotations
import pytest
from archon.agents.parser import parse_agent_json, build_findings, build_artifacts, build_citations


class TestParseAgentJson:
    def test_valid_json(self):
        raw = '{"findings": [{"title": "test"}], "confidence": 0.8}'
        result = parse_agent_json(raw, "test")
        assert result["confidence"] == 0.8
        assert len(result["findings"]) == 1

    def test_json_with_markdown_fences(self):
        raw = '`json\n{"findings": [], "confidence": 0.5}\n`'
        result = parse_agent_json(raw, "test")
        assert result["confidence"] == 0.5

    def test_json_with_surrounding_text(self):
        raw = 'Here is my analysis:\n{"findings": [], "confidence": 0.6}\nDone.'
        result = parse_agent_json(raw, "test")
        assert result["confidence"] == 0.6

    def test_no_json_found(self):
        raw = "No JSON here at all"
        result = parse_agent_json(raw, "test")
        assert result["findings"] == []
        assert result["confidence"] == 0.3

    def test_trailing_comma_fix(self):
        raw = '{"findings": [{"title": "a"},], "confidence": 0.7,}'
        result = parse_agent_json(raw, "test")
        assert result["confidence"] == 0.7

    def test_empty_string(self):
        result = parse_agent_json("", "test")
        assert result["findings"] == []


class TestBuildFindings:
    def test_builds_valid_findings(self):
        data = {"findings": [
            {"title": "Issue", "description": "desc", "severity": "HIGH",
             "recommendation": "fix it", "confidence": 0.8}
        ]}
        findings = build_findings(data, "security")
        assert len(findings) == 1
        assert findings[0].domain == "security"
        assert findings[0].id.startswith("SEC")

    def test_auto_assigns_domain(self):
        data = {"findings": [
            {"title": "Issue", "description": "d", "severity": "LOW",
             "recommendation": "r", "confidence": 0.5}
        ]}
        findings = build_findings(data, "cloud-architect")
        assert findings[0].domain == "cloud-architect"

    def test_skips_malformed(self):
        data = {"findings": [
            {"title": "Good", "description": "d", "severity": "LOW",
             "recommendation": "r", "confidence": 0.5},
            {"bad_field_only": True},
        ]}
        findings = build_findings(data, "test")
        assert len(findings) == 1

    def test_empty_findings(self):
        findings = build_findings({}, "test")
        assert findings == []

    def test_severity_normalization(self):
        data = {"findings": [
            {"title": "x", "description": "d", "severity": "high",
             "recommendation": "r", "confidence": 0.5}
        ]}
        findings = build_findings(data, "test")
        assert findings[0].severity.value == "HIGH"


class TestBuildArtifacts:
    def test_builds_valid_artifacts(self):
        data = {"artifacts": [
            {"id": "a1", "artifact_type": "ADR", "title": "Use PG",
             "content": "# ADR", "filename": "adr.md"}
        ]}
        artifacts = build_artifacts(data)
        assert len(artifacts) == 1

    def test_skips_malformed(self):
        data = {"artifacts": [{"bad": True}]}
        artifacts = build_artifacts(data)
        assert artifacts == []

    def test_empty(self):
        assert build_artifacts({}) == []


class TestBuildCitations:
    def test_builds_from_search_results(self):
        class FakeResult:
            url = "https://example.com"
            title = "Example"
            excerpt = "An excerpt"
            published_date = "2024-01-01"
            score = 0.9
        citations = build_citations([FakeResult()])
        assert len(citations) == 1
        assert citations[0].credibility_score == 0.9

    def test_truncates_long_excerpt(self):
        class FakeResult:
            url = "https://example.com"
            title = "Example"
            excerpt = "x" * 500
            score = 0.5
        citations = build_citations([FakeResult()])
        assert len(citations[0].excerpt) <= 300

    def test_empty_list(self):
        assert build_citations([]) == []
