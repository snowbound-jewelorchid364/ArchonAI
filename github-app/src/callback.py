"""GitHub webhook entrypoint and review callback routes."""
from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/webhooks/github")
async def github_webhook(request: Request) -> JSONResponse:
    from .app import handle_pull_request_event, verify_signature

    signature = request.headers.get("X-Hub-Signature-256", "")
    payload_bytes = await request.body()
    if not verify_signature(payload_bytes, signature):
        return JSONResponse(status_code=403, content={"detail": "Invalid signature"})

    event_type = request.headers.get("X-GitHub-Event", "")
    payload = json.loads(payload_bytes or b"{}")

    if event_type != "pull_request":
        return JSONResponse(status_code=200, content={"status": "ignored", "event": event_type})

    if payload.get("action") not in {"opened", "synchronize"}:
        return JSONResponse(status_code=200, content={"status": "ignored", "action": payload.get("action")})

    body, status_code = await handle_pull_request_event(payload)
    return JSONResponse(status_code=status_code, content=body)


@router.post("/callbacks/review-complete")
async def review_complete(request: Request) -> JSONResponse:
    from .app import post_review_comment_with_retry

    data = await request.json()
    installation_id = data.get("metadata", {}).get("installation_id")
    repo_full_name = data.get("repo_full_name", "")
    pr_number = data.get("metadata", {}).get("pr_number")
    body = data.get("comment_body") or "## ARCHON PR Review\n\nReview completed."

    if not all([installation_id, repo_full_name, pr_number]):
        return JSONResponse(status_code=400, content={"detail": "Missing required fields"})

    ok = await post_review_comment_with_retry(
        installation_id=installation_id,
        repo_full_name=repo_full_name,
        pr_number=pr_number,
        body=body,
    )
    if not ok:
        logger.error("Failed to post callback comment for %s#%s", repo_full_name, pr_number)
        return JSONResponse(status_code=200, content={"status": "comment_failed"})
    return JSONResponse(status_code=200, content={"status": "comment_posted", "pr_number": pr_number})
