from __future__ import annotations
from ..core.ports.vector_store_port import VectorStorePort, DocumentChunk
from ..config.settings import settings


class RAGRetriever:
    def __init__(self, vector_store: VectorStorePort) -> None:
        self._store = vector_store

    async def retrieve(self, query: str, top_k: int | None = None) -> list[DocumentChunk]:
        k = top_k or settings.rag_top_k
        return await self._store.query(query, top_k=k)

    async def retrieve_as_context(self, query: str) -> str:
        chunks = await self.retrieve(query)
        if not chunks:
            return "No relevant codebase context found."
        parts = []
        for chunk in chunks:
            parts.append(f"### {chunk.file_path}\n{chunk.content}")
        return "\n\n---\n\n".join(parts)
