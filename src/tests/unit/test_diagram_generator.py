from src.archon.output.diagram_generator import MermaidDiagramGenerator, MermaidNode, MermaidEdge


def test_flowchart():
    gen = MermaidDiagramGenerator()
    nodes = [
        MermaidNode(id="A", label="API"),
        MermaidNode(id="B", label="DB", type="database"),
    ]
    edges = [MermaidEdge(source="A", target="B", label="SQL")]
    result = gen.flowchart("test", nodes, edges)
    assert "flowchart LR" in result
    assert "A[API]" in result
    assert "B[(DB)]" in result
    assert "-->|SQL|" in result


def test_max_nodes():
    gen = MermaidDiagramGenerator()
    nodes = [MermaidNode(id=f"n{i}", label=f"Node{i}") for i in range(20)]
    result = gen.flowchart("test", nodes, [])
    assert "n14" in result
    assert "n15" not in result


def test_c4_context():
    gen = MermaidDiagramGenerator()
    nodes = [MermaidNode(id="ext", label="GitHub", type="external")]
    result = gen.c4_context("System", nodes, [])
    assert "System_Ext" in result
