from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from api.schemas.auth import CurrentUser
from archon.health.scorer import get_score_history, get_latest_score
from db.models import HealthScoreRow

router = APIRouter(prefix="/health-score", tags=["health-score"])


def _score_to_dict(row: HealthScoreRow) -> dict:
    return {
        "id": row.id,
        "review_id": row.review_id,
        "repo_url": row.repo_url,
        "overall": row.overall,
        "domains": {
            "software": row.software,
            "cloud": row.cloud,
            "security": row.security,
            "data": row.data,
            "integration": row.integration,
            "ai": row.ai,
        },
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


@router.get("/{repo_url:path}/latest")
async def get_latest_health_score(
    repo_url: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    score = await get_latest_score(db, current_user.user_id, repo_url)
    if score is None:
        raise HTTPException(status_code=404, detail="No health score found for this repo")
    return _score_to_dict(score)


@router.get("/{repo_url:path}/history")
async def list_health_score_history(
    repo_url: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(default=30, ge=1, le=100),
) -> list[dict]:
    scores = await get_score_history(db, current_user.user_id, repo_url, limit=limit)
    return [_score_to_dict(s) for s in scores]
