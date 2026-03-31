"""pgvector adapter implementing VectorStorePort."""
from __future__ import annotations

import json
import logging
from typing import Any

from archon.core.ports.vector_store_port import VectorStorePort

logger = logging.getLogger(__name__)


class PgVectorStore(VectorStorePort):
    """PostgreSQL + pgvector vector store."""

    def __init__(self, connection_string: str, collection: str = "archon_embeddings"):
        self._dsn = connection_string
        self._collection = collection
        self._pool = None

    async def _ensure_pool(self) -> None:
        if self._pool is not None:
            return
        try:
            import asyncpg
        except ImportError:
            raise RuntimeError("asyncpg required: uv pip install asyncpg")
        self._pool = await asyncpg.create_pool(self._dsn, min_size=2, max_size=10)
        table = self._collection
        async with self._pool.acquire() as conn:
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    metadata JSONB DEFAULT '{{}}',
                    embedding vector(384),
                    project_id TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            await conn.execute(
                f"CREATE INDEX IF NOT EXISTS idx_{table}_proj ON {table}(project_id)"
            )
        logger.info("pgvector store ready: %s", table)

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
        async with self._pool.acquire() as conn:
            for did, doc, emb, meta in zip(ids, documents, embeddings, metadatas):
                await conn.execute(
                    f"INSERT INTO {t}(id,content,metadata,embedding,project_id) "
                    f"VALUES(,,,::vector,) "
                    f"ON CONFLICT(id) DO UPDATE SET content=,metadata=,embedding=::vector",
                    did, doc, json.dumps(meta), str(emb), project_id,
                )

    async def query(
        self,
        query_embedding: list[float],
        n_results: int = 5,
        project_id: str = "default",
    ) -> list[dict[str, Any]]:
        await self._ensure_pool()
        t = self._collection
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                f"SELECT id,content,metadata,1-(embedding<=>::vector) AS sim "
                f"FROM {t} WHERE project_id= ORDER BY embedding<=>::vector LIMIT ",
                str(query_embedding), project_id, n_results,
            )
        return [
            {
                "id": r["id"],
                "content": r["content"],
                "metadata": json.loads(r["metadata"]) if r["metadata"] else {},
                "similarity": float(r["sim"]),
            }
            for r in rows
        ]

    async def delete_collection(self, project_id: str = "default") -> None:
        await self._ensure_pool()
        async with self._pool.acquire() as conn:
            await conn.execute(
                f"DELETE FROM {self._collection} WHERE project_id=", project_id
            )
        logger.info("Deleted vectors for project: %s", project_id)
