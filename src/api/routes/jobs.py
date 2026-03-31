from __future__ import annotations
import asyncio
import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from ..schemas.auth import CurrentUser
from ..dependencies import require_user
from ..services.review_service import get_job

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{job_id}/status")
async def get_job_status(
    job_id: str,
    user: CurrentUser = Depends(require_user),
) -> dict:
    job = await get_job(job_id, user.user_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": job.id,
        "review_id": job.review_id,
        "status": job.status,
        "progress": job.progress,
    }


@router.get("/{job_id}/stream")
async def stream_job_progress(
    job_id: str,
    user: CurrentUser = Depends(require_user),
) -> StreamingResponse:
    async def event_generator():
        last_status = None
        retries = 0
        max_retries = 360  # 60 min at 10s intervals

        while retries < max_retries:
            job = await get_job(job_id, user.user_id)
            if not job:
                yield f"event: error\ndata: {json.dumps({'error': 'Job not found'})}\n\n"
                return

            current = {
                "job_id": job.id,
                "status": job.status,
                "progress": job.progress or {},
            }

            if json.dumps(current) != last_status:
                last_status = json.dumps(current)
                yield f"event: progress\ndata: {last_status}\n\n"

            if job.status in {"COMPLETED", "FAILED", "PARTIAL"}:
                yield f"event: done\ndata: {json.dumps({'status': job.status, 'review_id': job.review_id})}\n\n"
                return

            await asyncio.sleep(10)
            retries += 1

        yield f"event: timeout\ndata: {json.dumps({'error': 'Stream timed out'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
