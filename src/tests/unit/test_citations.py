from src.archon.output.citations import CitationConsolidator
from src.archon.core.models.finding import Citation


def test_deduplicate():
    c = CitationConsolidator()
    citations = [
        Citation(url="https://a.com", title="A", excerpt="e1", credibility_score=0.7),
        Citation(url="https://a.com", title="A", excerpt="e2", credibility_score=0.9),
        Citation(url="https://b.com", title="B", excerpt="e3", credibility_score=0.8),
    ]
    result = c.deduplicate(citations)
    assert len(result) == 2
    assert result[0].credibility_score == 0.9


def test_deduplicate_empty():
    c = CitationConsolidator()
    assert c.deduplicate([]) == []
