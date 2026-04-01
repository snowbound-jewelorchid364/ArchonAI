"""Tests for RAG indexer and retriever."""
from __future__ import annotations
import pytest
from unittest.mock import AsyncMock, MagicMock
from archon.rag.indexer import RAGIndexer
from archon.rag.retriever import RAGRetriever
from archon.core.ports.repo_port import RepoFile
from archon.core.ports.vector_store_port import DocumentChunk


class TestRAGIndexer:
    @pytest.mark.asyncio
    async def test_index_calls_repo_and_store(self, mock_repo_reader):
        store = MagicMock()
        store.index = AsyncMock()
        indexer = RAGIndexer(mock_repo_reader, store)
        count = await indexer.index("/tmp/test")
        mock_repo_reader.get_files.assert_called_once_with("/tmp/test")
        store.index.assert_called_once()
        assert count > 0

    @pytest.mark.asyncio
    async def test_index_returns_chunk_count(self, mock_repo_reader):
        store = MagicMock()
        store.index = AsyncMock()
        indexer = RAGIndexer(mock_repo_reader, store)
        count = await indexer.index("/tmp/test")
        assert isinstance(count, int)
        assert count >= 1


class TestRAGRetriever:
    @pytest.mark.asyncio
    async def test_retrieve_calls_store(self, sample_chunks):
        store = MagicMock()
        store.query = AsyncMock(return_value=sample_chunks[:2])
        retriever = RAGRetriever(store)
        results = await retriever.retrieve("security patterns")
        store.query.assert_called_once()
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_retrieve_as_context_returns_string(self, sample_chunks):
        store = MagicMock()
        store.query = AsyncMock(return_value=sample_chunks[:1])
        retriever = RAGRetriever(store)
        ctx = await retriever.retrieve_as_context("query")
        assert isinstance(ctx, str)
        assert "main.py" in ctx

    @pytest.mark.asyncio
    async def test_retrieve_as_context_empty(self):
        store = MagicMock()
        store.query = AsyncMock(return_value=[])
        retriever = RAGRetriever(store)
        ctx = await retriever.retrieve_as_context("query")
        assert "No relevant" in ctx

    @pytest.mark.asyncio
    async def test_retrieve_custom_top_k(self, sample_chunks):
        store = MagicMock()
        store.query = AsyncMock(return_value=sample_chunks)
        retriever = RAGRetriever(store)
        await retriever.retrieve("query", top_k=3)
        store.query.assert_called_once_with("query", top_k=3)
