from __future__ import annotations
import json
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from api.schemas.auth import CurrentUser
from db.models import ReviewRow

logger = logging.getLogger(__name__)

router = APIRouter(tags=["intake"])


class StartIntakeRequest(BaseModel):
    idea: str


class SubmitIntakeRequest(BaseModel):
    idea: str
    answers: dict[str, str]


@router.post("/start", summary="Stream intake questions for Idea Mode")
async def start_intake(
    body: StartIntakeRequest,
    user: CurrentUser = Depends(get_current_user),
) -> StreamingResponse:
    """Stream the 6 intake questions as SSE events.

    Events:
    - {"type": "question", "key": "users", "data": "...", "index": 1, "total": 6}
    - {"type": "ready", "data": "Great! Starting your architecture..."}
    """
    from archon.engine.intake import stream_all_questions

    if not body.idea or not body.idea.strip():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="idea is required")

    return StreamingResponse(
        stream_all_questions(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/submit", summary="Submit intake answers and kick off Idea Mode pipeline")
async def submit_intake(
    body: SubmitIntakeRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Validate answers, create a review, enqueue the Idea Mode job, and return IDs."""
    from archon.engine.intake import run_intake, INTAKE_QUESTIONS

    if not body.idea or not body.idea.strip():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="idea is required")

    required_keys = {k for k, _ in INTAKE_QUESTIONS}
    missing = required_keys - set(body.answers.keys())
    if missing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Missing answers for: {sorted(missing)}",
        )

    try:
        brief = await run_intake(body.idea, body.answers)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    # Encode idea in repo_url field (no real repo for Idea Mode)
    repo_url = f"idea:{body.idea[:80]}"
    review_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())

    row = ReviewRow(
        id=review_id,
        user_id=user.user_id,
        repo_url=repo_url,
        mode="idea_mode",
        status="QUEUED",
    )
    db.add(row)

    # Non-fatal: enqueue job if Redis is available
    try:
        import redis.asyncio as aioredis
        from archon.config.settings import settings

        payload = json.dumps({
            "review_id": review_id,
            "user_id": user.user_id,
            "repo_url": repo_url,
            "mode": "idea_mode",
            "job_id": job_id,
            "brief": brief.model_dump(),
        })
        r = aioredis.from_url(settings.redis_url, decode_responses=True)
        await r.rpush("archon:jobs", payload)
        await r.aclose()
    except Exception as exc:
        logger.warning("Could not enqueue idea_mode job: %s", exc)

    return {"review_id": review_id, "job_id": job_id}
