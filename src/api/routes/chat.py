"""Architecture Chat API route — POST /api/v1/reviews/{review_id}/chat"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from api.schemas.auth import CurrentUser
from api.schemas.chat import ChatHistoryResponse, ChatMessageOut, ChatRequest
from archon.chat.engine import stream_chat
from archon.chat.history import get_history
from db.models import ReviewRow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reviews/{review_id}/chat", tags=["chat"])


@router.post("", summary="Send a message to the architecture advisor")
async def chat_message(
    review_id: str,
    body: ChatRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Stream a grounded architecture chat response via SSE.

    Each SSE event is a JSON object:
    - ``{"type": "text", "data": "chunk"}`` — partial response text
    - ``{"type": "done", "data": ""}``  — stream complete
    - ``{"type": "error", "data": "msg"}`` — error occurred
    """
    result = await db.execute(
        select(ReviewRow).where(
            ReviewRow.id == review_id,
            ReviewRow.user_id == user.user_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    return StreamingResponse(
        stream_chat(db, review_id, body.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("", response_model=ChatHistoryResponse, summary="Get chat history for a review")
async def get_chat_history(
    review_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatHistoryResponse:
    result = await db.execute(
        select(ReviewRow).where(
            ReviewRow.id == review_id,
            ReviewRow.user_id == user.user_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    messages = await get_history(db, review_id)
    return ChatHistoryResponse(
        review_id=review_id,
        messages=[ChatMessageOut(**m.model_dump()) for m in messages],
    )
