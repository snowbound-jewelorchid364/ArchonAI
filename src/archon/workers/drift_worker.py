from __future__ import annotations

import json
import logging
import uuid

from src.api.workers.review_worker import process_review
from src.archon.memory.snapshot import get_snapshots, save_snapshot
from src.db.connection import get_session
from src.db.models import ReviewRow

logger = logging.getLogger(__name__)


async def run_drift_check(repo_url: str, user_id: str) -> str:
    review_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())

    previous_snapshot = None
    async with get_session() as session:
        snapshots = await get_snapshots(session, user_id=user_id, repo_url=repo_url, limit=1)
        if snapshots:
            previous_snapshot = snapshots[0]

    memory_context = ""
    if previous_snapshot is not None:
        memory_context = (
            "## Previous Architecture Snapshot\n"
            f"Snapshot ID: {previous_snapshot.id}\n"
            f"Summary: {previous_snapshot.summary}\n"
        )

    logger.info(
        "Starting drift check for repo=%s user=%s previous_snapshot=%s",
        repo_url,
        user_id,
        getattr(previous_snapshot, "id", "none"),
    )

    await process_review(
        review_id=review_id,
        job_id=job_id,
        repo_url=repo_url,
        mode="drift_monitor",
        user_id=user_id,
    )

    async with get_session() as session:
        result = await session.get(ReviewRow, review_id)
        if result and result.package_json:
            from archon.core.models.review_package import ReviewPackage

            package = ReviewPackage.model_validate(result.package_json)
            await save_snapshot(session, user_id=user_id, review_id=review_id, package=package)
            await session.commit()

    return job_id


def schedule_weekly_drift() -> object:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger

    scheduler = AsyncIOScheduler(timezone="UTC")

    scheduler.add_job(
        lambda: logger.info("Weekly drift scheduler tick"),
        trigger=CronTrigger(day_of_week="mon", hour=8, minute=0),
        id="archon-weekly-drift",
        replace_existing=True,
    )
    scheduler.start()
    return scheduler

