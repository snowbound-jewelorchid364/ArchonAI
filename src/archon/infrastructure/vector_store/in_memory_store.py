from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np
from ...core.ports.vector_store_port import VectorStorePort, DocumentChunk

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer


class InMemoryVectorStore(VectorStorePort):

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self._model_name = model_name
        self._model: SentenceTransformer | None = None
        self._chunks: list[DocumentChunk] = []
        self._embeddings: np.ndarray | None = None

    def _get_model(self) -> SentenceTransformer:
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self._model_name)
        return self._model

    async def index(self, chunks: list[DocumentChunk]) -> None:
        self._chunks = chunks
        texts = [c.content for c in chunks]
        model = self._get_model()
        self._embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)

    async def query(self, query: str, top_k: int = 5) -> list[DocumentChunk]:
        if self._embeddings is None or len(self._chunks) == 0:
            return []
        model = self._get_model()
        query_vec = model.encode([query], convert_to_numpy=True)
        scores = np.dot(self._embeddings, query_vec.T).flatten()
        norms = np.linalg.norm(self._embeddings, axis=1) * np.linalg.norm(query_vec)
        cosine_scores = scores / (norms + 1e-8)
        top_indices = np.argsort(cosine_scores)[::-1][:top_k]
        return [self._chunks[i] for i in top_indices]

    async def clear(self) -> None:
        self._chunks = []
        self._embeddings = None
