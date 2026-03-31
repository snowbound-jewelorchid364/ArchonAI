"""ARCHON GitHub App - Webhook handler for PR reviews."""
import hashlib
import hmac
import logging
import os
from typing import Any

import httpx
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

app = FastAPI(title="ARCHON GitHub App", version="0.1.0")

from .callback import router as callback_router
app.include_router(callback_router)


GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")
ARCHON_API_URL = os.getenv("ARCHON_API_URL", "https://api.archon.dev")
ARCHON_INTERNAL_KEY = os.getenv("ARCHON_INTERNAL_KEY", "")


class PREvent(BaseModel):
    """Parsed pull request event."""
    action: str
    repo_full_name: str
    repo_url: str
    pr_number: int
    pr_title: str
    pr_branch: str
    base_branch: str
    installation_id: int


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature (HMAC-SHA256)."""
    if not GITHUB_WEBHOOK_SECRET:
        logger.warning("GITHUB_WEBHOOK_SECRET not set - skipping verification")
        return True

    expected = "sha256=" + hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def parse_pr_event(payload: dict[str, Any]) -> PREvent | None:
    """Parse a pull_request webhook payload."""
    action = payload.get("action", "")
    if action not in ("opened", "synchronize", "reopened"):
        return None

    pr = payload.get("pull_request", {})
    repo = payload.get("repository", {})
    installation = payload.get("installation", {})

    return PREvent(
        action=action,
        repo_full_name=repo.get("full_name", ""),
        repo_url=repo.get("html_url", ""),
        pr_number=pr.get("number", 0),
        pr_title=pr.get("title", ""),
        pr_branch=pr.get("head", {}).get("ref", ""),
        base_branch=pr.get("base", {}).get("ref", ""),
        installation_id=installation.get("id", 0),
    )


async def trigger_pr_review(event: PREvent) -> str:
    """Trigger an ARCHON PR review via the API."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{ARCHON_API_URL}/api/v1/reviews",
            json={
                "repo_url": event.repo_url,
                "mode": "pr_reviewer",
                "hitl_mode": "autopilot",
                "metadata": {
                    "pr_number": event.pr_number,
                    "pr_branch": event.pr_branch,
                    "base_branch": event.base_branch,
                    "installation_id": event.installation_id,
                },
            },
            headers={
                "Authorization": f"Bearer {ARCHON_INTERNAL_KEY}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("job_id", "unknown")


async def post_review_comment(
    installation_id: int,
    repo_full_name: str,
    pr_number: int,
    findings: list[dict],
) -> None:
    """Post review findings as a PR comment."""
    severity_emoji = {
        "CRITICAL": "\U0001f534",
        "HIGH": "\U0001f7e0",
        "MEDIUM": "\U0001f7e1",
        "LOW": "\U0001f7e2",
        "INFO": "\U0001f535",
    }

    lines = ["## ARCHON Architecture Review\n"]
    lines.append(f"Found **{len(findings)}** findings:\n")

    for f in findings:
        emoji = severity_emoji.get(f.get("severity", "INFO"), "")
        lines.append(f"- {emoji} **{f.get('severity')}**: {f.get('title')}")
        if f.get("file"):
            lines.append(f"  - File: `{f['file']}`")
        lines.append(f"  - {f.get('recommendation', '')}")
        lines.append("")

    lines.append("\n---\n*Powered by [ARCHON](https://archon.dev)*")

    body = "\n".join(lines)

    token = await get_installation_token(installation_id)
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments",
            json={"body": body},
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=30.0,
        )


async def get_installation_token(installation_id: int) -> str:
    """Get GitHub App installation token using JWT."""
    import jwt
    import time

    app_id = os.getenv("GITHUB_APP_ID", "")
    private_key = os.getenv("GITHUB_APP_PRIVATE_KEY", "")

    now = int(time.time())
    payload = {
        "iat": now - 60,
        "exp": now + (10 * 60),
        "iss": app_id,
    }
    encoded = jwt.encode(payload, private_key, algorithm="RS256")

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"https://api.github.com/app/installations/{installation_id}/access_tokens",
            headers={
                "Authorization": f"Bearer {encoded}",
                "Accept": "application/vnd.github+json",
            },
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json()["token"]


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "app": "archon-github-app"}


@app.post("/webhooks/github")
async def github_webhook(request: Request):
    """Handle GitHub webhook events."""
    # Verify signature
    signature = request.headers.get("X-Hub-Signature-256", "")
    payload_bytes = await request.body()

    if not verify_signature(payload_bytes, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event_type = request.headers.get("X-GitHub-Event", "")
    payload = await request.json()

    if event_type == "pull_request":
        event = parse_pr_event(payload)
        if event:
            logger.info(
                f"PR event: {event.action} #{event.pr_number} on {event.repo_full_name}"
            )
            try:
                job_id = await trigger_pr_review(event)
                return {"status": "review_triggered", "job_id": job_id}
            except Exception as e:
                logger.error(f"Failed to trigger review: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    if event_type == "installation":
        action = payload.get("action", "")
        logger.info(f"Installation event: {action}")
        return {"status": "ok", "action": action}

    return {"status": "ignored", "event": event_type}
