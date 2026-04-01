import pytest
from archon.core.models.finding import Finding, Severity, Citation
from archon.core.models.agent_output import AgentOutput
from archon.core.models.review_package import ReviewPackage
from archon.output.citations import CitationConsolidator
from archon.output.confidence import ConfidenceScorer
from archon.output.diagram_generator import MermaidDiagramGenerator, MermaidNode, MermaidEdge


def _make_citation(url="https://example.com/article"):
    return Citation(url=url, title="Source Article", excerpt="relevant excerpt", credibility_score=0.7)


def _make_finding(severity=Severity.HIGH, domain="software", title="Test Finding", cites=True):
    return Finding(
        id=domain[:2].upper() + "-001",
        title=title,
        severity=severity,
        description="Test finding description",
        recommendation="Fix the issue",
        domain=domain,
        confidence=0.8,
        from_codebase=True,
        citations=[_make_citation()] if cites else [],
    )


def _make_package(findings=None, mode="review"):
    return ReviewPackage(
        run_id="test-001",
        repo_url="https://github.com/test/repo",
        mode=mode,
        duration_seconds=30.0,
        executive_summary="Test summary",
        findings=findings if findings is not None else [_make_finding()],
    )


class TestCitationConsolidator:
    def test_dedup_same_url(self):
        consolidator = CitationConsolidator()
        c1 = _make_citation("https://example.com/a")
        c2 = _make_citation("https://example.com/a")
        result = consolidator.deduplicate([c1, c2])
        assert len(result) == 1

    def test_keeps_different_urls(self):
        consolidator = CitationConsolidator()
        c1 = _make_citation("https://example.com/a")
        c2 = _make_citation("https://example.com/b")
        result = consolidator.deduplicate([c1, c2])
        assert len(result) == 2

    def test_sorted_by_credibility(self):
        consolidator = CitationConsolidator()
        c1 = Citation(url="https://example.com/a", title="Low", excerpt="x", credibility_score=0.3)
        c2 = Citation(url="https://example.com/b", title="High", excerpt="x", credibility_score=0.9)
        result = consolidator.deduplicate([c1, c2])
        assert result[0].credibility_score > result[1].credibility_score

    def test_from_package(self):
        consolidator = CitationConsolidator()
        package = _make_package()
        result = consolidator.from_package(package)
        assert len(result) >= 1


class TestConfidenceScorer:
    def test_score_finding(self):
        scorer = ConfidenceScorer()
        finding = _make_finding()
        score = scorer.score_finding(finding)
        assert 0.0 <= score <= 1.0

    def test_score_finding_no_citations(self):
        scorer = ConfidenceScorer()
        finding = _make_finding(cites=False)
        score = scorer.score_finding(finding)
        assert 0.0 <= score <= 1.0

    def test_score_agent(self):
        scorer = ConfidenceScorer()
        output = AgentOutput(domain="software", findings=[_make_finding()], confidence=0.85, duration_seconds=10.0)
        score = scorer.score_agent(output)
        assert 0.0 <= score <= 1.0

    def test_score_agent_no_findings(self):
        scorer = ConfidenceScorer()
        output = AgentOutput(domain="software", findings=[], confidence=0.0, duration_seconds=5.0)
        score = scorer.score_agent(output)
        assert score == 0.0

    def test_score_package(self):
        scorer = ConfidenceScorer()
        package = _make_package()
        score = scorer.score_package(package)
        assert 0.0 <= score <= 1.0

    def test_score_package_empty(self):
        scorer = ConfidenceScorer()
        package = _make_package(findings=[])
        score = scorer.score_package(package)
        assert score == 0.0


class TestMermaidDiagramGenerator:
    def test_c4_context(self):
        gen = MermaidDiagramGenerator()
        nodes = [MermaidNode(id="web", label="Web App"), MermaidNode(id="db", label="Database", type="database")]
        edges = [MermaidEdge(source="web", target="db", label="reads", protocol="SQL")]
        result = gen.c4_context("Test System", nodes, edges)
        assert "C4Context" in result
        assert "Test System" in result
        assert "web" in result

    def test_flowchart(self):
        gen = MermaidDiagramGenerator()
        nodes = [MermaidNode(id="A", label="Service A"), MermaidNode(id="B", label="Service B")]
        edges = [MermaidEdge(source="A", target="B", label="calls")]
        result = gen.flowchart("Data Flow", nodes, edges)
        assert "flowchart" in result
        assert "Service A" in result

    def test_max_nodes_enforced(self):
        gen = MermaidDiagramGenerator()
        nodes = [MermaidNode(id=f"n{i}", label=f"Node {i}") for i in range(20)]
        edges = []
        result = gen.c4_context("Big System", nodes, edges)
        node_count = result.count("System(")
        assert node_count <= gen.MAX_NODES
