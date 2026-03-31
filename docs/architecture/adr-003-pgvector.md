# ADR-003: pgvector Over Dedicated Vector Database

**Status:** Accepted
**Date:** 2026-03-31
**Deciders:** ARCHON founding team

---

## Context

ARCHON indexes user codebases as vector embeddings for RAG-based context injection into agent runs. We need a vector store. Options: dedicated vector databases (Pinecone, Qdrant, Weaviate) or pgvector (PostgreSQL extension).

---

## Decision

Use **pgvector** as the vector store, running inside the same PostgreSQL instance used for relational data.

---

## Rationale

**Operational simplicity.** pgvector eliminates an entire infrastructure dependency. One database to back up, one connection pool to manage, one monitoring dashboard. At MVP, every additional service is a liability.

**Hybrid search in one query.** ARCHON uses hybrid search combining semantic similarity (cosine via HNSW) and keyword search (BM25 via tsvector). With pgvector in Postgres, this is a single SQL query with RRF scoring. With an external vector DB, it requires two separate calls and client-side merging.

**Transactional consistency.** When a project is deleted, `ON DELETE CASCADE` removes its code chunks atomically with all other project data. With an external vector DB, this requires coordinating two deletion operations.

**Scale is sufficient for MVP.** pgvector's HNSW index performs well up to tens of millions of vectors. ARCHON's MVP target is thousands of projects with average repo size of ~50k lines. At 512-token chunks, that's ~100 chunks per 10k lines = ~500k vectors at 10k projects. Well within pgvector's range.

---

## Consequences

- PostgreSQL requires pgvector extension: `CREATE EXTENSION IF NOT EXISTS "pgvector"`
- HNSW index parameters need tuning: `m=16, ef_construction=64` for recall vs. build time balance
- Embedding dimension is fixed per model — changing models requires re-indexing all vectors
- `code_chunks` table will be the largest table; partitioning by `project_id` if it grows beyond 50M rows

---

## Migration Seam

If this decision needs to be reversed (e.g., query volume exceeds pgvector's performance envelope), the `rag/retriever.py` interface abstracts the vector store behind a `search(query: str, project_id: UUID, top_k: int) -> list[CodeChunk]` method. Swapping the implementation requires changes in one file.

---

## Alternatives Rejected

**Qdrant:** Better ANN performance at scale and a richer filtering API. Rejected for MVP due to the additional infrastructure dependency. Revisit at 10M+ vectors.

**Pinecone:** Managed, no ops. Rejected due to cloud vendor dependency, per-vector pricing, and data residency concerns (user code leaves our infrastructure).

**Weaviate:** Full-featured, hybrid search built-in. Rejected: too much for MVP, significant operational complexity.
