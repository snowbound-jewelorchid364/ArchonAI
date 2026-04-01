"""Chat message persistence."""
from __future__ import annotations

import uuid
from datetime import datetime, UTC

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import ChatMessageRow


class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    review_id: str
    role: str  # "user" | "assistant"
    content: str
    citations: list[dict] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


async def save_message(
    db: AsyncSession,
    review_id: str,
    role: str,
    content: str,
    citations: list[dict] | None = None,
) -> ChatMessage:
    row = ChatMessageRow(
        id=str(uuid.uuid4()),
        review_id=review_id,
        role=role,
        content=content,
        citations=citations or [],
    )
    db.add(row)
    await db.flush()
    return ChatMessage(
        id=row.id,
        review_id=row.review_id,
        role=row.role,
        content=row.content,
        citations=row.citations or [],
        created_at=row.created_at,
    )


async def get_history(
    db: AsyncSession,
    review_id: str,
    limit: int = 20,
) -> list[ChatMessage]:
    result = await db.execute(
        select(ChatMessageRow)
        .where(ChatMessageRow.review_id == review_id)
        .order_by(ChatMessageRow.created_at.desc())
        .limit(limit)
    )
    rows = result.scalars().all()
    return [
        ChatMessage(
            id=row.id,
            review_id=row.review_id,
            role=row.role,
            content=row.content,
            citations=row.citations or [],
            created_at=row.created_at,
        )
        for row in reversed(rows)  # return in chronological order
    ]
