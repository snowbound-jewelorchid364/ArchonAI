from src.archon.output.confidence import ConfidenceScorer
from src.archon.core.models.finding import Finding, Severity, Citation


def make_finding(severity=Severity.HIGH, confidence=0.8, citations=None, from_codebase=True):
    return Finding(
        id="f1", title="Test", description="desc", severity=severity,
        domain="security", recommendation="Fix it",
        citations=citations or [], confidence=confidence, from_codebase=from_codebase
    )


def test_score_finding_no_citations():
    scorer = ConfidenceScorer()
    f = make_finding(confidence=0.9)
    assert scorer.score_finding(f) == 0.9


def test_score_finding_with_citations():
    scorer = ConfidenceScorer()
    c = Citation(url="https://example.com", title="T", excerpt="E", credibility_score=0.95)
    f = make_finding(confidence=0.8, citations=[c])
    score = scorer.score_finding(f)
    assert 0.8 < score < 0.95


def test_score_finding_not_from_codebase_penalty():
    scorer = ConfidenceScorer()
    f1 = make_finding(confidence=0.8, from_codebase=True)
    f2 = make_finding(confidence=0.8, from_codebase=False)
    assert scorer.score_finding(f2) < scorer.score_finding(f1)


def test_grade():
    scorer = ConfidenceScorer()
    assert scorer.grade(0.95) == "A"
    assert scorer.grade(0.8) == "B"
    assert scorer.grade(0.65) == "C"
    assert scorer.grade(0.45) == "D"
    assert scorer.grade(0.2) == "F"
