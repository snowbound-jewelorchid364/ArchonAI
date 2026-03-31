from __future__ import annotations
import hashlib
import hmac
import logging
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/github")
async def github_webhook(request: Request) -> JSONResponse:
    from archon.config.settings import settings

    payload = await request.body()

    # Verify GitHub webhook signature if secret is set
    webhook_secret = getattr(settings, "github_webhook_secret", "")
    if webhook_secret:
        signature = request.headers.get("X-Hub-Signature-256", "")
        expected = "sha256=" + hmac.new(
            webhook_secret.encode(), payload, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

    event_type = request.headers.get("X-GitHub-Event", "")
    data = await request.json()

    if event_type == "pull_request":
        action = data.get("action", "")
        if action in {"opened", "synchronize"}:
            pr = data.get("pull_request", {})
            repo_url = data.get("repository", {}).get("html_url", "")
            pr_number = pr.get("number")
            logger.info("PR %s#%s — queuing PR Reviewer", repo_url, pr_number)
            # TODO: enqueue PR Reviewer job
            return JSONResponse(
                status_code=202,
                content={"message": f"PR #{pr_number} review queued"},
            )

    return JSONResponse(status_code=200, content={"message": "Event received"})
