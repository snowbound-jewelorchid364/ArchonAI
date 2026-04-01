"""Chat API request/response schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000, description="User's message to the architecture advisor")


class ChatMessageOut(BaseModel):
    id: str
    review_id: str
    role: str
    content: str
    citations: list[dict] = Field(default_factory=list)
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    review_id: str
    messages: list[ChatMessageOut]
