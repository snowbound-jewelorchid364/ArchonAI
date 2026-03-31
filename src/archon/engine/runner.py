from __future__ import annotations
import logging
import uuid

from ..core.models.job import Job, JobStatus
from ..core.models.review_package import ReviewPackage
from .supervisor import Supervisor
from .hitl.checkpoints import HITLMode

logger = logging.getLogger(__name__)


class Runner:
    def __init__(self, supervisor: Supervisor) -> None:
        self._supervisor = supervisor

    async def run(
        self,
        repo_url: str,
        mode: str = 'review',
        job_id: str | None = None,
        hitl_mode: HITLMode = HITLMode.AUTOPILOT,
    ) -> tuple[Job, ReviewPackage]:
        job_id = job_id or str(uuid.uuid4())
        job = Job(id=job_id, repo_url=repo_url, mode=mode, status=JobStatus.RUNNING)
        logger.info('Job %s started | mode=%s repo=%s hitl=%s', job_id, mode, repo_url, hitl_mode.value)

        try:
            package = await self._supervisor.run(
                repo_url=repo_url, mode=mode, job_id=job_id, hitl_mode=hitl_mode,
            )
            if package.partial:
                job.status = JobStatus.PARTIAL
            else:
                job.status = JobStatus.COMPLETED
            job.finding_count = len(package.all_findings())
            logger.info('Job %s completed | %d findings', job_id, job.finding_count)
            return job, package
        except Exception as exc:
            logger.exception('Job %s failed: %s', job_id, exc)
            job.status = JobStatus.FAILED
            job.error = str(exc)
            raise
