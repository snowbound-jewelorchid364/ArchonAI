from __future__ import annotations
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch
from archon.core.models.agent_output import AgentOutput
from archon.core.models.finding import Finding, Severity
from archon.engine.supervisor import Supervisor


@pytest.mark.asyncio
async def test_supervisor_merges_all_agent_outputs(mock_llm, mock_searcher, tmp_path):
    from archon.infrastructure.vector_store.in_memory_store import InMemoryVectorStore
    from archon.rag.retriever import RAGRetriever

    store = InMemoryVectorStore()
    retriever = RAGRetriever(vector_store=store)

    mock_output = AgentOutput(
        domain="software",
        findings=[
            Finding(
                id="f1", title="Test finding", description="desc",
                severity=Severity.HIGH, domain="software",
                recommendation="fix it", confidence=0.9, from_codebase=True,
            )
        ],
        confidence=0.85,
        duration_seconds=5.0,
    )

    supervisor = Supervisor(llm=mock_llm, searchers=[mock_searcher], retriever=retriever)

    with patch.object(supervisor, "_run_agents", return_value=[mock_output] * 6):
        package = await supervisor.run(repo_path=tmp_path, mode="review", job_id="test-123")

    assert package is not None
    assert len(package.all_findings()) > 0


@pytest.mark.asyncio
async def test_supervisor_handles_agent_failure(mock_llm, mock_searcher, tmp_path):
    from archon.infrastructure.vector_store.in_memory_store import InMemoryVectorStore
    from archon.rag.retriever import RAGRetriever

    store = InMemoryVectorStore()
    retriever = RAGRetriever(vector_store=store)

    failed_output = AgentOutput(
        domain="cloud", confidence=0.0, duration_seconds=1.0,
        error="Simulated failure", partial=True,
    )

    supervisor = Supervisor(llm=mock_llm, searchers=[mock_searcher], retriever=retriever)

    with patch.object(supervisor, "_run_agents", return_value=[failed_output] * 6):
        package = await supervisor.run(repo_path=tmp_path, mode="review", job_id="fail-test")

    assert package.partial is True
