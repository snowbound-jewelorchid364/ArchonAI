"""Tests for BaseArchitectAgent."""
from __future__ import annotations
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from archon.agents.base import BaseArchitectAgent
from archon.core.models.agent_output import AgentOutput
from archon.rag.retriever import RAGRetriever


class ConcreteAgent(BaseArchitectAgent):
    domain = "test-agent"
    _prompt_path = "nonexistent.md"

    async def _analyse(self, repo_context: str, mode: str, *, mode_focus: str = "") -> AgentOutput:
        return AgentOutput(
            domain=self.domain,
            findings=[],
            confidence=0.8,
            duration_seconds=1.0,
        )


class SlowAgent(BaseArchitectAgent):
    domain = "slow-agent"
    _prompt_path = "nonexistent.md"

    async def _analyse(self, repo_context: str, mode: str, *, mode_focus: str = "") -> AgentOutput:
        await asyncio.sleep(100)
        return AgentOutput(domain=self.domain, confidence=0.5, duration_seconds=0.0)


class FailingAgent(BaseArchitectAgent):
    domain = "failing-agent"
    _prompt_path = "nonexistent.md"

    async def _analyse(self, repo_context: str, mode: str, *, mode_focus: str = "") -> AgentOutput:
        raise RuntimeError("Agent crashed")


class TestBaseArchitectAgent:
    @pytest.mark.asyncio
    async def test_run_returns_output(self, mock_llm, mock_searcher):
        store = MagicMock()
        store.query = AsyncMock(return_value=[])
        retriever = RAGRetriever(store)
        agent = ConcreteAgent(mock_llm, [mock_searcher], retriever)
        output = await agent.run("review")
        assert output.domain == "test-agent"
        assert output.confidence == 0.8
        assert output.partial is False

    @pytest.mark.asyncio
    async def test_run_timeout_returns_partial(self, mock_llm, mock_searcher):
        store = MagicMock()
        store.query = AsyncMock(return_value=[])
        retriever = RAGRetriever(store)
        agent = SlowAgent(mock_llm, [mock_searcher], retriever)
        with patch("archon.config.settings.settings.agent_timeout_seconds", 0.01):
            output = await agent.run("review")
        assert output.partial is True
        assert "timed out" in output.error

    @pytest.mark.asyncio
    async def test_run_exception_returns_partial(self, mock_llm, mock_searcher):
        store = MagicMock()
        store.query = AsyncMock(return_value=[])
        retriever = RAGRetriever(store)
        agent = FailingAgent(mock_llm, [mock_searcher], retriever)
        output = await agent.run("review")
        assert output.partial is True
        assert "crashed" in output.error

    @pytest.mark.asyncio
    async def test_search_collects_from_multiple_searchers(self, mock_llm):
        s1 = MagicMock()
        s1.search = AsyncMock(return_value=["result1"])
        s2 = MagicMock()
        s2.search = AsyncMock(return_value=["result2"])
        store = MagicMock()
        store.query = AsyncMock(return_value=[])
        retriever = RAGRetriever(store)
        agent = ConcreteAgent(mock_llm, [s1, s2], retriever)
        results = await agent._search("test query")
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_search_handles_failure(self, mock_llm):
        s1 = MagicMock()
        s1.search = AsyncMock(side_effect=Exception("API down"))
        store = MagicMock()
        store.query = AsyncMock(return_value=[])
        retriever = RAGRetriever(store)
        agent = ConcreteAgent(mock_llm, [s1], retriever)
        results = await agent._search("test query")
        assert results == []

    def test_load_prompt_fallback(self, mock_llm, mock_searcher):
        store = MagicMock()
        store.query = AsyncMock(return_value=[])
        retriever = RAGRetriever(store)
        agent = ConcreteAgent(mock_llm, [mock_searcher], retriever)
        assert "test-agent" in agent._system_prompt
