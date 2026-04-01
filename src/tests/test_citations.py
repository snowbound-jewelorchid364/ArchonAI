"""Tests for CitationConsolidator."""
from __future__ import annotations
import pytest
from archon.output.citations import CitationConsolidator
from archon.core.models.finding import Citation


class TestCitationConsolidator:
    def test_deduplicate_removes_dupes(self):
        c = CitationConsolidator()
        citations = [
            Citation(url="https://example.com/a", title="A", excerpt="excerpt a", credibility_score=0.8),
            Citation(url="https://example.com/a", title="A dup", excerpt="excerpt a dup", credibility_score=0.9),
            Citation(url="https://example.com/b", title="B", excerpt="excerpt b", credibility_score=0.7),
        ]
        result = c.deduplicate(citations)
        assert len(result) == 2
        urls = [str(r.url) for r in result]
        assert "https://example.com/a" in urls[0] or "https://example.com/a/" in urls[0]

    def test_deduplicate_keeps_higher_credibility(self):
        c = CitationConsolidator()
        citations = [
            Citation(url="https://example.com/x", title="Low", excerpt="e", credibility_score=0.3),
            Citation(url="https://example.com/x", title="High", excerpt="e", credibility_score=0.95),
        ]
        result = c.deduplicate(citations)
        assert len(result) == 1
        assert result[0].credibility_score == 0.95

    def test_deduplicate_empty(self):
        c = CitationConsolidator()
        assert c.deduplicate([]) == []

    def test_from_package(self, sample_package):
        c = CitationConsolidator()
        result = c.from_package(sample_package)
        assert len(result) > 0

    def test_by_domain(self, sample_package):
        c = CitationConsolidator()
        result = c.by_domain(sample_package)
        assert isinstance(result, dict)

    def test_stats(self, sample_package):
        c = CitationConsolidator()
        stats = c.stats(sample_package)
        assert "total_unique" in stats
        assert "avg_credibility" in stats
        assert "domains_covered" in stats
        assert "high_credibility" in stats
        assert isinstance(stats["total_unique"], int)