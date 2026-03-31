# ADR-007: Phase 1 RAG Strategy — In-Memory Vector Store

**Status:** Accepted
**Date:** 2026-03-31

---

## Context

ARCHON needs to give agents context from the user's codebase. Production uses pgvector. Phase 1 is a CLI — no database, no infrastructure dependencies.

---

## Decision

Phase 1 uses an **in-memory vector store** with `sentence-transformers/all-MiniLM-L6-v2` for local embeddings (no API call for embeddings).

```
Files → Chunks → Local embeddings → numpy array → cosine search
```

---

## Implementation

```python
# rag/store.py
import numpy as np
from sentence_transformers import SentenceTransformer

class InMemoryVectorStore:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.chunks: list[CodeChunk] = []
        self.embeddings: np.ndarray | None = None

    def index(self, chunks: list[CodeChunk]) -> None:
        texts = [c.content for c in chunks]
        self.embeddings = self.model.encode(texts, batch_size=32, show_progress_bar=True)
        self.chunks = chunks

    def search(self, query: str, top_k: int = 10) -> list[CodeChunk]:
        query_embedding = self.model.encode([query])
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        top_indices = np.argsort(similarities)[::-1][:top_k]
        return [self.chunks[i] for i in top_indices]
```

---

## Chunking Strategy

```python
# rag/chunker.py
# Priority order:
# 1. tree-sitter AST boundaries (Python, JavaScript, TypeScript, Go)
# 2. Class/function-level splitting
# 3. Line-based fallback (512 lines max, 50 overlap) for other languages

SUPPORTED_LANGUAGES = ["python", "javascript", "typescript", "go"]
MAX_CHUNK_TOKENS = 512
OVERLAP_LINES = 20
```

Files skipped:
- `node_modules/`, `.git/`, `dist/`, `build/`, `__pycache__/`
- `*.lock`, `*.min.js`, `*.min.css`
- Binary files, images, videos
- Files > 1000 lines (split at function boundaries)

---

## Phase 1 Upgrade Path

Phase 1 replaces `InMemoryVectorStore` with `PgVectorStore` that implements the same `index()` and `search()` interface. No agent code changes required.

```python
# Phase 1: rag/store.py → rag/pg_store.py
class PgVectorStore:
    async def index(self, chunks: list[CodeChunk]) -> None: ...
    async def search(self, query: str, top_k: int = 10) -> list[CodeChunk]: ...
```

---

## Consequences

- **No database required** for Phase 1 — single process, all in memory
- Model download on first run (~90MB for all-MiniLM-L6-v2)
- Indexing speed: ~100ms per 100 files on modern hardware
- Search quality: adequate for Phase 1 validation (not production-grade)
- Memory: ~500MB for a 50k LOC repo
- Not persisted between runs — re-indexes every time (acceptable for Phase 1)

---

## Alternatives Rejected

**Voyage AI API for embeddings (Phase 1):** Requires API call per chunk, adds cost, adds network dependency. Overkill for CLI PoC.

**Chroma DB (Phase 1):** Adds a file-based DB dependency. Simpler than pgvector but still an external dependency. In-memory numpy is simpler.

**No RAG (Phase 1):** Agents could work from file tree + agent system prompts alone. But the whole point of Phase 1 is to validate RAG quality. Skip RAG = skip the core value proposition.
