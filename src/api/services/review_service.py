from __future__ import annotations
import uuid
import logging
from datetime import datetime, UTC
from sqlalchemy import select, update
from src.db.connection import get_session
from src.db.models import ReviewRow, JobRow, UserRow

logger = logging.getLogger(__name__)

PLAN_LIMITS = {"starter": 3, "pro": 999_999, "team": 999_999}


async def check_plan_limit(user_id: str) -> tuple[bool, str]:
    async with get_session() as session:
        user = await session.get(UserRow, user_id)
        if not user:
            return False, "User not found"
        limit = PLAN_LIMITS.get(user.plan, 3)
        if user.runs_this_month >= limit:
            return False, f"Plan limit reached ({user.runs_this_month}/{limit}). Upgrade at /billing."
        return True, "OK"


async def create_review(user_id: str, repo_url: str, mode: str) -> tuple[str, str]:
    review_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())

    async with get_session() as session:
        review = ReviewRow(
            id=review_id,
            user_id=user_id,
            repo_url=repo_url,
            mode=mode,
            status="QUEUED",
        )
        job = JobRow(
            id=job_id,
            review_id=review_id,
            user_id=user_id,
            status="QUEUED",
            progress={"agents": {}},
        )
        session.add(review)
        session.add(job)

        await session.execute(
            update(UserRow).where(UserRow.id == user_id).values(
                runs_this_month=UserRow.runs_this_month + 1
            )
        )

    return review_id, job_id


async def get_review(review_id: str, user_id: str) -> ReviewRow | None:
    async with get_session() as session:
        result = await session.execute(
            select(ReviewRow).where(
                ReviewRow.id == review_id,
                ReviewRow.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()


async def list_reviews(user_id: str, limit: int = 20, offset: int = 0) -> list[ReviewRow]:
    async with get_session() as session:
        result = await session.execute(
            select(ReviewRow)
            .where(ReviewRow.user_id == user_id)
            .order_by(ReviewRow.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())


async def update_review_status(
    review_id: str,
    status: str,
    *,
    finding_count: int = 0,
    critical_count: int = 0,
    high_count: int = 0,
    confidence: float = 0.0,
    duration_seconds: float = 0.0,
    cost_usd: float = 0.0,
    package_json: dict | None = None,
    agent_statuses: dict | None = None,
    executive_summary: str | None = None,
    error: str | None = None,
    partial: bool = False,
) -> None:
    async with get_session() as session:
        values: dict = {"status": status}
        if status in {"COMPLETED", "PARTIAL", "FAILED"}:
            values["completed_at"] = datetime.now(UTC)
        if finding_count:
            values["finding_count"] = finding_count
        if critical_count:
            values["critical_count"] = critical_count
        if high_count:
            values["high_count"] = high_count
        if confidence:
            values["confidence"] = confidence
        if duration_seconds:
            values["duration_seconds"] = duration_seconds
        if cost_usd:
            values["cost_usd"] = cost_usd
        if package_json is not None:
            values["package_json"] = package_json
        if agent_statuses is not None:
            values["agent_statuses"] = agent_statuses
        if executive_summary is not None:
            values["executive_summary"] = executive_summary
        if error is not None:
            values["error"] = error
        values["partial"] = partial

        await session.execute(
            update(ReviewRow).where(ReviewRow.id == review_id).values(**values)
        )


async def update_job_progress(job_id: str, status: str, progress: dict | None = None) -> None:
    async with get_session() as session:
        values: dict = {"status": status, "updated_at": datetime.now(UTC)}
        if progress is not None:
            values["progress"] = progress
        await session.execute(
            update(JobRow).where(JobRow.id == job_id).values(**values)
        )


async def get_job(job_id: str, user_id: str) -> JobRow | None:
    async with get_session() as session:
        result = await session.execute(
            select(JobRow).where(JobRow.id == job_id, JobRow.user_id == user_id)
        )
        return result.scalar_one_or_none()
