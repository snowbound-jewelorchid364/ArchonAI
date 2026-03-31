"""Finding feedback API route."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_current_user
from api.schemas.feedback import FeedbackCreate, FeedbackResponse, FeedbackSummary

router = APIRouter(prefix="/reviews/{review_id}/feedback", tags=["feedback"])

# In-memory store for MVP; replace with DB in production
_feedback_store: dict[str, list[dict]] = {}


@router.post("", response_model=FeedbackResponse)
async def submit_feedback(
    review_id: str,
    body: FeedbackCreate,
    user: dict = Depends(get_current_user),
) -> FeedbackResponse:
    fb = {
        "id": str(uuid.uuid4()),
        "review_id": review_id,
        "finding_id": body.finding_id,
        "helpful": body.helpful,
        "comment": body.comment,
        "user_id": user.get("sub", "anon"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _feedback_store.setdefault(review_id, []).append(fb)
    return FeedbackResponse(**fb)


@router.get("", response_model=FeedbackSummary)
async def get_feedback_summary(
    review_id: str,
    user: dict = Depends(get_current_user),
) -> FeedbackSummary:
    items = _feedback_store.get(review_id, [])
    return FeedbackSummary(
        review_id=review_id,
        total=len(items),
        helpful_count=sum(1 for i in items if i["helpful"]),
        unhelpful_count=sum(1 for i in items if not i["helpful"]),
        comments=[i["comment"] for i in items if i["comment"]],
    )
