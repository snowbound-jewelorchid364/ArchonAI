"""pgvector adapter implementing VectorStorePort.

Uses asyncpg with proper $N numbered placeholders for parameterised queries.
Table name is validated to prevent SQL injection.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any

from archon.core.ports.vector_store_port import VectorStorePort

logger = logging.getLogger(__name__)

_SAFE_TABLE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]{0,62}$")


def _validate_table(name: str) -> str:
    if not _SAFE_TABLE.match(name):
        raise ValueError(f"Invalid table name: {name!r}")
    return name


class PgVectorStore(VectorStorePort):
    """PostgreSQL + pgvector vector store."""

    def __init__(self, connection_string: str, collection: str = "archon_embeddings"):
        self._dsn = connection_string
        self._collection = _validate_table(collection)
        self._pool = None

    async def _ensure_pool(self) -> None:
        if self._pool is not None:
            return
        try:
            import asyncpg
        except ImportError:
            raise RuntimeError("asyncpg required: uv pip install asyncpg")
        self._pool = await asyncpg.create_pool(self._dsn, min_size=2, max_size=10)
        t = self._collection
        async with self._pool.acquire() as conn:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {t} (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    metadata JSONB DEFAULT '{{}}'::jsonb,
                    embedding vector(384),
                    project_id TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            await conn.execute(
                f"CREATE INDEX IF NOT EXISTS idx_{t}_proj ON {t}(project_id)"
            )
            await conn.execute(
                f"CREATE INDEX IF NOT EXISTS idx_{t}_emb ON {t} "
                f"USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
            )
        logger.info("pgvector store ready: %s", t)

    async def add_documents(
        self,
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]] | None = None,
        ids: list[str] | None = None,
        project_id: str = "default",
    ) -> None:
        await self._ensure_pool()
        metadatas = metadatas or [{} for _ in documents]
        ids = ids or [f"doc_{i}" for i in range(len(documents))]
        t = self._collection
        sql = (
            f"INSERT INTO {t}(id, content, metadata, embedding, project_id) "
            f"VALUES($1, $2, $3, $4::vector, $5) "
            f"ON CONFLICT(id) DO UPDATE SET content=$2, metadata=$3, embedding=$4::vector"
        )
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                for did, doc, emb, meta in zip(ids, documents, embeddings, metadatas):
                    await conn.execute(
                        sql, did, doc, json.dumps(meta), str(emb), project_id
                    )

    async def query(
        self,
        query_embedding: list[float],
        n_results: int = 5,
        project_id: str = "default",
    ) -> list[dict[str, Any]]:
        await self._ensure_pool()
        t = self._collection
        sql = (
            f"SELECT id, content, metadata, "
            f"1 - (embedding <=> $1::vector) AS similarity "
            f"FROM {t} WHERE project_id = $2 "
            f"ORDER BY embedding <=> $1::vector LIMIT $3"
        )
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(sql, str(query_embedding), project_id, n_results)
        return [
            {
                "id": r["id"],
                "content": r["content"],
                "metadata": json.loads(r["metadata"]) if r["metadata"] else {},
                "similarity": float(r["similarity"]),
            }
            for r in rows
        ]

    async def index(self, chunks: list) -> None:
        """Index DocumentChunk objects (VectorStorePort interface)."""
        from archon.core.ports.vector_store_port import DocumentChunk
        docs = [c.content for c in chunks]
        metas = [{"file_path": c.file_path, **c.metadata} for c in chunks]
        ids = [c.id for c in chunks]
        # Embeddings must be provided externally; use zero vectors as placeholder
        embeddings = [[0.0] * 384 for _ in chunks]
        await self.add_documents(docs, embeddings, metas, ids)

    async def clear(self) -> None:
        """Clear all documents from the collection (VectorStorePort interface)."""
        await self._ensure_pool()
        async with self._pool.acquire() as conn:
            await conn.execute(f"TRUNCATE {self._collection}")
        logger.info("Cleared collection: %s", self._collection)

    async def delete_collection(self, project_id: str = "default") -> None:
        await self._ensure_pool()
        async with self._pool.acquire() as conn:
            await conn.execute(
                f"DELETE FROM {self._collection} WHERE project_id = $1", project_id
            )
        logger.info("Deleted vectors for project: %s", project_id)

    async def count(self, project_id: str = "default") -> int:
        await self._ensure_pool()
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                f"SELECT COUNT(*) AS cnt FROM {self._collection} WHERE project_id = $1",
                project_id,
            )
        return int(row["cnt"]) if row else 0
