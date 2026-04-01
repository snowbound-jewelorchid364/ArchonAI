"""ARCHON GitHub App - Webhook handler for PR reviews."""
from __future__ import annotations

import hashlib
import hmac
import logging
import os
import time
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from archon.core.models import ReviewPackage
from archon.output.sections.pr_reviewer import render_pr_github_comment

logger = logging.getLogger(__name__)

app = FastAPI(title="ARCHON GitHub App", version="0.1.0")

from .callback import router as callback_router

app.include_router(callback_router)


GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")
ARCHON_API_URL = os.getenv("ARCHON_API_URL", "https://api.archon.dev")
ARCHON_INTERNAL_KEY = os.getenv("ARCHON_INTERNAL_KEY", "")


class PREvent(BaseModel):
    action: str
    repo_full_name: str
    repo_url: str
    pr_number: int
    pr_title: str
    pr_branch: str
    base_branch: str
    installation_id: int


def verify_signature(payload: bytes, signature: str) -> bool:
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


async def trigger_pr_review(event: PREvent, pr_diff: str) -> tuple[str, str]:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{ARCHON_API_URL}/api/v1/reviews",
            json={
                "repo_url": event.repo_url,
                "mode": "pr_reviewer",
                "brief": f"PR title: {event.pr_title}\n\nPR diff:\n{pr_diff[:20000]}",
            },
            headers={
                "Authorization": f"Bearer {ARCHON_INTERNAL_KEY}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("review_id", ""), data.get("job_id", "")


async def fetch_pr_diff(installation_id: int, repo_full_name: str, pr_number: int) -> str:
    token = await get_installation_token(installation_id)
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3.diff",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.text


async def wait_for_review_result(review_id: str, job_id: str, timeout_seconds: int = 120) -> dict[str, Any] | None:
    deadline = time.monotonic() + timeout_seconds
    async with httpx.AsyncClient() as client:
        while time.monotonic() < deadline:
            status_resp = await client.get(
                f"{ARCHON_API_URL}/api/v1/jobs/{job_id}/status",
                headers={"Authorization": f"Bearer {ARCHON_INTERNAL_KEY}"},
                timeout=15.0,
            )
            if status_resp.status_code == 200:
                status_data = status_resp.json()
                if status_data.get("status") in {"COMPLETED", "PARTIAL", "FAILED"}:
                    break
            await asyncio_sleep(3)

        review_resp = await client.get(
            f"{ARCHON_API_URL}/api/v1/reviews/{review_id}",
            headers={"Authorization": f"Bearer {ARCHON_INTERNAL_KEY}"},
            timeout=20.0,
        )
        if review_resp.status_code != 200:
            return None
        return review_resp.json()


async def asyncio_sleep(seconds: int) -> None:
    import asyncio

    await asyncio.sleep(seconds)


async def post_review_comment(
    installation_id: int,
    repo_full_name: str,
    pr_number: int,
    body: str,
) -> None:
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
    import jwt

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
async def health() -> dict[str, str]:
    return {"status": "ok", "app": "archon-github-app"}


@app.post("/webhooks/github")
async def github_webhook(request: Request) -> dict[str, str]:
    signature = request.headers.get("X-Hub-Signature-256", "")
    payload_bytes = await request.body()

    if not verify_signature(payload_bytes, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event_type = request.headers.get("X-GitHub-Event", "")
    payload = await request.json()

    if event_type == "pull_request":
        event = parse_pr_event(payload)
        if event:
            logger.info("PR event: %s #%s on %s", event.action, event.pr_number, event.repo_full_name)
            try:
                pr_diff = await fetch_pr_diff(event.installation_id, event.repo_full_name, event.pr_number)
                review_id, job_id = await trigger_pr_review(event, pr_diff)
                review_detail = await wait_for_review_result(review_id, job_id, timeout_seconds=120)

                if review_detail is None:
                    timeout_body = (
                        "## ARCHON PR Review\n\n"
                        "Review timed out after 2 minutes. Partial analysis may still complete in ARCHON."
                    )
                    await post_review_comment(event.installation_id, event.repo_full_name, event.pr_number, timeout_body)
                    return {"status": "timeout", "review_id": review_id}

                package = ReviewPackage(
                    run_id=review_id,
                    repo_url=event.repo_url,
                    mode="pr_reviewer",
                    duration_seconds=float(review_detail.get("duration_seconds") or 0),
                    executive_summary=review_detail.get("executive_summary") or "",
                    findings=[],
                    artifacts=[],
                    citations=[],
                    agent_statuses=review_detail.get("agent_statuses") or {},
                    partial=bool(review_detail.get("partial", False)),
                    model_version="",
                )
                comment_body = render_pr_github_comment(package)
                await post_review_comment(event.installation_id, event.repo_full_name, event.pr_number, comment_body)
                return {"status": "review_posted", "review_id": review_id}
            except Exception as exc:
                logger.error("Failed PR review flow: %s", exc)
                raise HTTPException(status_code=500, detail=str(exc))

    if event_type == "installation":
        action = payload.get("action", "")
        logger.info("Installation event: %s", action)
        return {"status": "ok", "action": action}

    return {"status": "ignored", "event": event_type}
