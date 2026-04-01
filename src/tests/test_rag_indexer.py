from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from archon.core.ports.repo_port import RepoFile
from archon.core.ports.vector_store_port import DocumentChunk
from archon.rag.indexer import RAGIndexer
from archon.rag.retriever import RAGRetriever


class FixtureRepoReader:
    def __init__(self, root: Path) -> None:
        self.root = root

    async def clone(self, repo_url: str, job_id: str) -> str:
        return str(self.root)

    async def get_files(self, repo_path: str) -> list[RepoFile]:
        files: list[RepoFile] = []
        for p in self.root.rglob("*.py"):
            text = p.read_text(encoding="utf-8")
            rel = p.relative_to(self.root).as_posix()
            files.append(RepoFile(path=rel, content=text, size_bytes=len(text)))
        return files

    async def count_loc(self, repo_path: str) -> int:
        total = 0
        for p in self.root.rglob("*.py"):
            total += len(p.read_text(encoding="utf-8").splitlines())
        return total

    async def cleanup(self, repo_path: str) -> None:
        return None


@pytest.mark.asyncio
async def test_rag_indexer_indexes_fixture_repo_and_stores_nonempty_chunks() -> None:
    fixture_root = Path(__file__).parent / "fixtures" / "sample_repos" / "python_fastapi"
    reader = FixtureRepoReader(fixture_root)

    captured_chunks: list[DocumentChunk] = []

    class Store:
        async def index(self, chunks: list[DocumentChunk]) -> None:
            captured_chunks.extend(chunks)

        async def query(self, query: str, top_k: int = 5) -> list[DocumentChunk]:
            return [c for c in captured_chunks if "auth" in c.content.lower() or "middleware" in c.content.lower()][:top_k]

        async def clear(self) -> None:
            captured_chunks.clear()

    store = Store()
    indexer = RAGIndexer(reader, store)

    chunk_count = await indexer.index(str(fixture_root))

    assert chunk_count > 0
    assert captured_chunks
    assert any(c.content.strip() for c in captured_chunks)


@pytest.mark.asyncio
async def test_rag_retriever_returns_authentication_middleware_relevant_context() -> None:
    store = MagicMock()
    store.query = AsyncMock(
        return_value=[
            DocumentChunk(
                id="c1",
                file_path="main.py",
                content="app.add_middleware(AuthenticationMiddleware)",
                metadata={"start_line": 1, "end_line": 1},
            )
        ]
    )
    retriever = RAGRetriever(store)

    chunks = await retriever.retrieve("authentication middleware")
    context = await retriever.retrieve_as_context("authentication middleware")

    assert len(chunks) == 1
    assert "AuthenticationMiddleware" in context
