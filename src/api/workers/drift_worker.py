from __future__ import annotations
import logging

from .review_worker import process_review

logger = logging.getLogger(__name__)


async def process_drift_job(job_data: dict) -> None:
    """Scheduled weekly drift monitor worker."""
    review_id = job_data.get("review_id", "drift-unknown")
    repo_url = job_data.get("repo_url", "")
    job_id = job_data.get("job_id", "drift-job")
    logger.info("Drift monitor triggered for review %s", review_id)
    await process_review(
        review_id=review_id,
        job_id=job_id,
        repo_url=repo_url,
        mode="drift_monitor",
    )
