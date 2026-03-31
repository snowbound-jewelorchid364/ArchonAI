from __future__ import annotations
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from ..schemas.review import ReviewRequest, ReviewResponse, ReviewDetail, ReviewListItem
from ..schemas.auth import CurrentUser
from ..dependencies import require_user
from ..services.review_service import create_review, get_review, list_reviews, check_plan_limit

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_MODES = {
    "review", "design", "migration_planner", "compliance_auditor", "due_diligence",
    "incident_responder", "cost_optimiser", "pr_reviewer", "scaling_advisor",
    "drift_monitor", "feature_feasibility", "vendor_evaluator",
    "onboarding_accelerator", "sunset_planner",
}


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_review_endpoint(
    body: ReviewRequest,
    user: CurrentUser = Depends(require_user),
) -> ReviewResponse:
    if body.mode not in ALLOWED_MODES:
        raise HTTPException(status_code=400, detail=f"Invalid mode: {body.mode}")

    repo = str(body.repo_url)
    if not repo.startswith("https://github.com/"):
        raise HTTPException(status_code=400, detail="Only github.com repos supported")

    allowed, reason = await check_plan_limit(user.user_id)
    if not allowed:
        raise HTTPException(status_code=402, detail=reason)

    review_id, job_id = await create_review(user.user_id, repo, body.mode)

    # TODO: enqueue to Redis worker
    # await redis.enqueue("archon:reviews", {"review_id": review_id, "job_id": job_id, ...})

    logger.info("Review %s queued (job %s) for user %s", review_id, job_id, user.user_id)
    return ReviewResponse(
        review_id=review_id,
        job_id=job_id,
        status="QUEUED",
        message="Review queued successfully",
    )


@router.get("", response_model=list[ReviewListItem])
async def list_reviews_endpoint(
    limit: int = 20,
    offset: int = 0,
    user: CurrentUser = Depends(require_user),
) -> list[ReviewListItem]:
    reviews = await list_reviews(user.user_id, limit=limit, offset=offset)
    return [
        ReviewListItem(
            id=r.id,
            repo_url=r.repo_url,
            mode=r.mode,
            status=r.status,
            finding_count=r.finding_count,
            critical_count=r.critical_count,
            high_count=r.high_count,
            created_at=r.created_at.isoformat(),
            completed_at=r.completed_at.isoformat() if r.completed_at else None,
        )
        for r in reviews
    ]


@router.get("/{review_id}", response_model=ReviewDetail)
async def get_review_endpoint(
    review_id: str,
    user: CurrentUser = Depends(require_user),
) -> ReviewDetail:
    review = await get_review(review_id, user.user_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return ReviewDetail(
        id=review.id,
        repo_url=review.repo_url,
        mode=review.mode,
        status=review.status,
        finding_count=review.finding_count,
        critical_count=review.critical_count,
        high_count=review.high_count,
        confidence=review.confidence,
        duration_seconds=review.duration_seconds,
        cost_usd=review.cost_usd,
        executive_summary=review.executive_summary,
        agent_statuses=review.agent_statuses,
        partial=review.partial,
        error=review.error,
        created_at=review.created_at.isoformat(),
        completed_at=review.completed_at.isoformat() if review.completed_at else None,
    )
