from __future__ import annotations
from ..core.ports.vector_store_port import VectorStorePort
from ..core.ports.repo_port import RepoPort
from .chunker import chunk_files
from ..config.settings import settings


class RAGIndexer:
    def __init__(self, repo_reader: RepoPort, vector_store: VectorStorePort) -> None:
        self._repo = repo_reader
        self._store = vector_store

    async def index(self, repo_path: str) -> int:
        files = await self._repo.get_files(repo_path)
        chunks = chunk_files(files)
        # Cap at 50k chunks for oversized repos
        if len(chunks) > 50_000:
            chunks = chunks[:50_000]
        await self._store.index(chunks)
        return len(chunks)
