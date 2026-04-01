"""Tests for SecurityArchitectAgent."""
from __future__ import annotations
import json
import pytest
from unittest.mock import AsyncMock, MagicMock
from archon.agents.security_architect import SecurityArchitectAgent
from archon.core.models.agent_output import AgentOutput
from archon.rag.retriever import RAGRetriever


def _mock_response():
    return json.dumps({
        "findings": [{
            "id": "SEC-001", "title": "Test finding",
            "description": "Test desc", "severity": "MEDIUM",
            "domain": "security-architect", "file_path": None,
            "line_number": None, "recommendation": "Fix it",
            "citations": [], "confidence": 0.7, "from_codebase": True
        }],
        "artifacts": [], "confidence": 0.7
    })


class TestSecurityArchitectAgent:
    def test_domain(self, mock_llm, mock_searcher):
        store = MagicMock()
        store.query = AsyncMock(return_value=[])
        agent = SecurityArchitectAgent(mock_llm, [mock_searcher], RAGRetriever(store))
        assert agent.domain == "security-architect"

    @pytest.mark.asyncio
    async def test_run_returns_output(self, mock_llm, mock_searcher):
        mock_llm.complete.return_value = _mock_response()
        store = MagicMock()
        store.query = AsyncMock(return_value=[])
        agent = SecurityArchitectAgent(mock_llm, [mock_searcher], RAGRetriever(store))
        output = await agent.run("review")
        assert isinstance(output, AgentOutput)
        assert output.domain == "security-architect"
        assert len(output.findings) == 1

    @pytest.mark.asyncio
    async def test_run_with_focus(self, mock_llm, mock_searcher):
        mock_llm.complete.return_value = _mock_response()
        store = MagicMock()
        store.query = AsyncMock(return_value=[])
        agent = SecurityArchitectAgent(mock_llm, [mock_searcher], RAGRetriever(store))
        output = await agent.run("review", mode_focus="test focus")
        assert isinstance(output, AgentOutput)

    @pytest.mark.asyncio
    async def test_run_error_returns_partial(self, mock_llm, mock_searcher):
        mock_llm.complete.side_effect = RuntimeError("API error")
        store = MagicMock()
        store.query = AsyncMock(return_value=[])
        agent = SecurityArchitectAgent(mock_llm, [mock_searcher], RAGRetriever(store))
        output = await agent.run("review")
        assert output.partial is True
        assert output.error is not None

    @pytest.mark.asyncio
    async def test_run_empty_findings(self, mock_llm, mock_searcher):
        mock_llm.complete.return_value = json.dumps({"findings": [], "artifacts": [], "confidence": 0.5})
        store = MagicMock()
        store.query = AsyncMock(return_value=[])
        agent = SecurityArchitectAgent(mock_llm, [mock_searcher], RAGRetriever(store))
        output = await agent.run("design")
        assert output.findings == []