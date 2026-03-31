"""Review history and diff API."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from db.models import Review

router = APIRouter(prefix="/reviews/history", tags=["history"])


@router.get("")
async def list_review_history(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all reviews for the current user, ordered by creation date."""
    user_id = user.get("sub", "")
    stmt = select(Review).where(Review.user_id == user_id).order_by(Review.created_at.desc())
    result = await db.execute(stmt)
    reviews = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "repo_url": r.repo_url,
            "mode": r.mode,
            "status": r.status,
            "finding_count": r.finding_count,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reviews
    ]


@router.get("/diff")
async def diff_reviews(
    review_a: str,
    review_b: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Compare findings between two reviews."""
    user_id = user.get("sub", "")

    stmt_a = select(Review).where(Review.id == review_a, Review.user_id == user_id)
    stmt_b = select(Review).where(Review.id == review_b, Review.user_id == user_id)

    ra = (await db.execute(stmt_a)).scalar_one_or_none()
    rb = (await db.execute(stmt_b)).scalar_one_or_none()

    if not ra or not rb:
        raise HTTPException(404, "One or both reviews not found")

    findings_a = set(ra.package_data.get("finding_ids", [])) if ra.package_data else set()
    findings_b = set(rb.package_data.get("finding_ids", [])) if rb.package_data else set()

    return {
        "review_a": review_a,
        "review_b": review_b,
        "added": list(findings_b - findings_a),
        "removed": list(findings_a - findings_b),
        "unchanged": list(findings_a & findings_b),
    }
