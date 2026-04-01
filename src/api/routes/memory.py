from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from api.schemas.auth import CurrentUser
from archon.memory.snapshot import get_snapshots
from archon.memory.decisions import get_decisions

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("/snapshots")
async def list_snapshots(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    repo_url: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[dict]:
    rows = await get_snapshots(db, current_user.user_id, repo_url=repo_url, limit=limit)
    return [
        {
            "id": r.id,
            "review_id": r.review_id,
            "repo_url": r.repo_url,
            "mode": r.mode,
            "summary": r.summary,
            "finding_count": r.finding_count,
            "critical_count": r.critical_count,
            "high_count": r.high_count,
            "domains": r.domains_json,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@router.get("/decisions")
async def list_decisions(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    repo_url: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[dict]:
    rows = await get_decisions(db, current_user.user_id, repo_url=repo_url, limit=limit)
    return [
        {
            "id": r.id,
            "review_id": r.review_id,
            "repo_url": r.repo_url,
            "adr_title": r.adr_title,
            "decision": r.decision,
            "rationale": r.rationale,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@router.get("/timeline")
async def architecture_timeline(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    repo_url: str = Query(...),
    limit: int = Query(default=40, ge=1, le=200),
) -> list[dict]:
    snapshots = await get_snapshots(db, current_user.user_id, repo_url=repo_url, limit=limit)
    decisions = await get_decisions(db, current_user.user_id, repo_url=repo_url, limit=limit)

    events: list[dict] = []
    for s in snapshots:
        events.append({
            "type": "snapshot",
            "id": s.id,
            "review_id": s.review_id,
            "repo_url": s.repo_url,
            "mode": s.mode,
            "summary": s.summary,
            "finding_count": s.finding_count,
            "critical_count": s.critical_count,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        })
    for d in decisions:
        events.append({
            "type": "decision",
            "id": d.id,
            "review_id": d.review_id,
            "repo_url": d.repo_url,
            "adr_title": d.adr_title,
            "decision": d.decision,
            "status": d.status,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        })

    events.sort(key=lambda e: e["created_at"] or "", reverse=True)
    return events[:limit]
