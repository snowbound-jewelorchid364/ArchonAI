"""Tests for MermaidDiagramGenerator."""
from __future__ import annotations
import pytest
from archon.output.diagram_generator import MermaidDiagramGenerator, MermaidNode, MermaidEdge


class TestMermaidDiagramGenerator:
    def test_c4_context_basic(self):
        gen = MermaidDiagramGenerator()
        nodes = [MermaidNode(id="api", label="API Server"), MermaidNode(id="db", label="Database", type="database")]
        edges = [MermaidEdge(source="api", target="db", label="queries", protocol="SQL")]
        result = gen.c4_context("System Context", nodes, edges)
        assert "C4Context" in result
        assert "System Context" in result
        assert "api" in result
        assert "SystemDb" in result

    def test_c4_context_external(self):
        gen = MermaidDiagramGenerator()
        nodes = [MermaidNode(id="ext", label="External API", type="external")]
        result = gen.c4_context("Test", nodes, [])
        assert "System_Ext" in result

    def test_c4_max_nodes(self):
        gen = MermaidDiagramGenerator()
        nodes = [MermaidNode(id=f"n{i}", label=f"Node {i}") for i in range(20)]
        result = gen.c4_context("Big", nodes, [])
        assert result.count("System(") <= 15

    def test_flowchart_basic(self):
        gen = MermaidDiagramGenerator()
        nodes = [MermaidNode(id="a", label="A"), MermaidNode(id="b", label="B", type="database")]
        edges = [MermaidEdge(source="a", target="b", label="reads")]
        result = gen.flowchart("Flow", nodes, edges)
        assert "flowchart LR" in result
        assert "a[A]" in result
        assert "b[(B)]" in result
        assert "|reads|" in result

    def test_flowchart_direction(self):
        gen = MermaidDiagramGenerator()
        result = gen.flowchart("Flow", [], [], direction="TD")
        assert "flowchart TD" in result

    def test_sequence_basic(self):
        gen = MermaidDiagramGenerator()
        result = gen.sequence("Seq", ["Client", "Server"], [("Client", "Server", "GET /api")])
        assert "sequenceDiagram" in result
        assert "participant Client" in result
        assert "GET /api" in result

    def test_flowchart_queue_type(self):
        gen = MermaidDiagramGenerator()
        nodes = [MermaidNode(id="q", label="Queue", type="queue")]
        result = gen.flowchart("Test", nodes, [])
        assert "q[[Queue]]" in result

    def test_flowchart_external_type(self):
        gen = MermaidDiagramGenerator()
        nodes = [MermaidNode(id="e", label="Ext", type="external")]
        result = gen.flowchart("Test", nodes, [])
        assert "e((Ext))" in result