"""Tests for SoftwareArchitectAgent."""
from __future__ import annotations
import json
import pytest
from unittest.mock import AsyncMock
from archon.agents.software_architect import SoftwareArchitectAgent
from archon.core.models.agent_output import AgentOutput
from archon.rag.retriever import RAGRetriever


def _mock_response(findings_count=1):
    findings = []
    for i in range(findings_count):
        findings.append({
            "id": f"SA-{i+1:03d}",
            "title": f"Finding {i+1}",
            "description": f"Description for finding {i+1}",
            "severity": "HIGH",
            "domain": "software-architect",
            "file_path": "api.py",
            "line_number": 10 + i,
            "recommendation": "Fix it",
            "citations": [],
            "confidence": 0.85,
            "from_codebase": True,
        })
    return json.dumps({"findings": findings, "artifacts": [], "confidence": 0.8})


@pytest.fixture
def sw_agent(mock_llm, mock_searcher):
    store = AsyncMock()
    store.query = AsyncMock(return_value=[])
    retriever = RAGRetriever(store)
    mock_llm.complete.return_value = _mock_response()
    return SoftwareArchitectAgent(mock_llm, [mock_searcher], retriever)


class TestSoftwareArchitectAgent:
    def test_domain(self, sw_agent):
        assert sw_agent.domain == "software-architect"

    @pytest.mark.asyncio
    async def test_run_returns_output(self, sw_agent):
        output = await sw_agent.run("review")
        assert isinstance(output, AgentOutput)
        assert output.domain == "software-architect"
        assert len(output.findings) == 1

    @pytest.mark.asyncio
    async def test_run_with_mode_focus(self, sw_agent):
        output = await sw_agent.run("review", mode_focus="error handling")
        assert isinstance(output, AgentOutput)

    @pytest.mark.asyncio
    async def test_run_empty_findings(self, mock_llm, mock_searcher):
        mock_llm.complete.return_value = json.dumps({"findings": [], "artifacts": [], "confidence": 0.5})
        store = AsyncMock()
        store.query = AsyncMock(return_value=[])
        agent = SoftwareArchitectAgent(mock_llm, [mock_searcher], RAGRetriever(store))
        output = await agent.run("design")
        assert output.findings == []

    @pytest.mark.asyncio
    async def test_run_llm_error(self, mock_llm, mock_searcher):
        mock_llm.complete.side_effect = RuntimeError("LLM down")
        store = AsyncMock()
        store.query = AsyncMock(return_value=[])
        agent = SoftwareArchitectAgent(mock_llm, [mock_searcher], RAGRetriever(store))
        output = await agent.run("review")
        assert output.partial is True
        assert output.error is not None

    @pytest.mark.asyncio
    async def test_multiple_findings(self, mock_llm, mock_searcher):
        mock_llm.complete.return_value = _mock_response(3)
        store = AsyncMock()
        store.query = AsyncMock(return_value=[])
        agent = SoftwareArchitectAgent(mock_llm, [mock_searcher], RAGRetriever(store))
        output = await agent.run("review")
        assert len(output.findings) == 3