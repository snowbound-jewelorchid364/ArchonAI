from __future__ import annotations
import pytest
from pathlib import Path
from archon.rag.chunker import Chunker
from archon.rag.indexer import RAGIndexer
from archon.rag.retriever import RAGRetriever
from archon.infrastructure.vector_store.in_memory_store import InMemoryVectorStore


@pytest.mark.asyncio
async def test_index_and_retrieve(small_repo: Path):
    store = InMemoryVectorStore()
    indexer = RAGIndexer(vector_store=store)
    await indexer.index(small_repo)

    assert store.count() > 0

    retriever = RAGRetriever(vector_store=store)
    context = await retriever.retrieve_as_context("hardcoded secrets security")
    assert len(context) > 0


@pytest.mark.asyncio
async def test_empty_repo_indexes_cleanly(tmp_path: Path):
    store = InMemoryVectorStore()
    indexer = RAGIndexer(vector_store=store)
    await indexer.index(tmp_path)
    assert store.count() == 0
