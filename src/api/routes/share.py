from __future__ import annotations
import secrets
from datetime import datetime, timedelta, UTC
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from src.db.connection import get_session
from src.db.models import ReviewRow, ShareLinkRow
from src.api.dependencies import get_current_user

router = APIRouter(prefix="/share", tags=["share"])


class CreateShareRequest(BaseModel):
    review_id: str
    expires_in_days: int = 30


class ShareLinkResponse(BaseModel):
    token: str
    url: str
    expires_at: str | None


@router.post("", response_model=ShareLinkResponse)
async def create_share_link(
    req: CreateShareRequest,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    review = await session.get(ReviewRow, req.review_id)
    if not review or review.user_id != user_id:
        raise HTTPException(404, "Review not found")
    if review.status != "COMPLETED":
        raise HTTPException(400, "Review must be completed before sharing")

    token = secrets.token_urlsafe(32)
    expires = datetime.now(UTC) + timedelta(days=req.expires_in_days)

    link = ShareLinkRow(
        review_id=req.review_id,
        user_id=user_id,
        token=token,
        expires_at=expires,
    )
    session.add(link)
    await session.commit()

    return ShareLinkResponse(
        token=token,
        url=f"/shared/{token}",
        expires_at=expires.isoformat(),
    )


@router.get("/{token}")
async def get_shared_review(
    token: str,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(ShareLinkRow).where(ShareLinkRow.token == token, ShareLinkRow.is_active == True)
    )
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(404, "Share link not found or expired")
    if link.expires_at and link.expires_at < datetime.now(UTC):
        raise HTTPException(410, "Share link has expired")

    review = await session.get(ReviewRow, link.review_id)
    if not review:
        raise HTTPException(404, "Review not found")

    # Flatten package_json fields to top level so frontend can consume directly
    pkg: dict = review.package_json or {}
    return {
        "run_id": pkg.get("run_id", review.id),
        "repo_url": review.repo_url,
        "mode": review.mode,
        "status": review.status,
        "partial": pkg.get("partial", review.partial if hasattr(review, "partial") else False),
        "created_at": review.created_at.isoformat(),
        "duration_seconds": pkg.get("duration_seconds", review.duration_seconds),
        "confidence": pkg.get("confidence", review.confidence),
        "finding_count": review.finding_count,
        "critical_count": review.critical_count,
        "high_count": review.high_count,
        "executive_summary": pkg.get("executive_summary", review.executive_summary or ""),
        "findings": pkg.get("findings", []),
        "artifacts": pkg.get("artifacts", []),
        "citations": pkg.get("citations", []),
        "agent_statuses": pkg.get("agent_statuses", review.agent_statuses or {}),
        "share_token": token,
    }


@router.delete("/{token}")
async def revoke_share_link(
    token: str,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(ShareLinkRow).where(ShareLinkRow.token == token, ShareLinkRow.user_id == user_id)
    )
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(404, "Share link not found")
    link.is_active = False
    await session.commit()
    return {"status": "revoked"}
