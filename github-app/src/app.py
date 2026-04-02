"""ARCHON GitHub App - webhook helpers and app wiring."""
from __future__ import annotations

import fnmatch
import hashlib
import hmac
import logging
import os
import time
from typing import Any

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

from archon.core.models import ReviewPackage
from archon.output.sections.pr_reviewer import render_pr_github_comment

from .callback import router as callback_router
from .repo_config import RepoConfig, decode_github_content, parse_repo_config

try:
    from anthropic import APIError as AnthropicAPIError
except ImportError:  # pragma: no cover - optional dependency in this package
    class AnthropicAPIError(Exception):
        pass

logger = logging.getLogger(__name__)

app = FastAPI(title="ARCHON GitHub App", version="0.1.0")
app.include_router(callback_router)

GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")
ARCHON_API_URL = os.getenv("ARCHON_API_URL", "https://api.archon.dev")
ARCHON_INTERNAL_KEY = os.getenv("ARCHON_INTERNAL_KEY", "")
REVIEW_RATE_LIMIT_SECONDS = 300
RECENT_PR_REVIEWS: dict[tuple[str, int], float] = {}


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
    if action not in {"opened", "synchronize", "reopened"}:
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


async def get_installation_token(installation_id: int) -> str:
    import jwt

    app_id = os.getenv("GITHUB_APP_ID", "")
    private_key = os.getenv("GITHUB_APP_PRIVATE_KEY", "")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + 600, "iss": app_id}
    encoded = jwt.encode(payload, private_key, algorithm="RS256")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.github.com/app/installations/{installation_id}/access_tokens",
            headers={
                "Authorization": f"Bearer {encoded}",
                "Accept": "application/vnd.github+json",
            },
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()["token"]


async def fetch_repo_config(installation_id: int, repo_full_name: str, ref: str) -> RepoConfig:
    token = await get_installation_token(installation_id)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com/repos/{repo_full_name}/contents/.archon.yml",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            params={"ref": ref},
            timeout=30.0,
        )
        if response.status_code == 404:
            return RepoConfig()
        response.raise_for_status()
        return parse_repo_config(decode_github_content(response.json()))


async def fetch_pr_diff(
    installation_id: int,
    repo_full_name: str,
    pr_number: int,
    repo_config: RepoConfig,
) -> str:
    token = await get_installation_token(installation_id)
    diff_chunks: list[str] = []
    included = 0
    page = 1

    async with httpx.AsyncClient() as client:
        while included < repo_config.max_files:
            response = await client.get(
                f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/files",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                params={"page": page, "per_page": min(100, repo_config.max_files)},
                timeout=30.0,
            )
            response.raise_for_status()
            files = response.json()
            if not files:
                break
            for file_info in files:
                filename = file_info.get("filename", "")
                if any(fnmatch.fnmatch(filename, pattern) for pattern in repo_config.ignore_patterns):
                    continue
                patch = file_info.get("patch")
                if not patch:
                    continue
                diff_chunks.append(f"diff --git a/{filename} b/{filename}\n{patch}\n")
                included += 1
                if included >= repo_config.max_files:
                    break
            page += 1

    return "\n".join(diff_chunks)


async def trigger_pr_review(event: PREvent, pr_diff: str) -> tuple[str, str]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
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
        response.raise_for_status()
        payload = response.json()
        return payload.get("review_id", ""), payload.get("job_id", "")


async def wait_for_review_result(review_id: str, job_id: str, timeout_seconds: int = 120) -> dict[str, Any] | None:
    deadline = time.monotonic() + timeout_seconds
    async with httpx.AsyncClient() as client:
        while time.monotonic() < deadline:
            status_response = await client.get(
                f"{ARCHON_API_URL}/api/v1/jobs/{job_id}/status",
                headers={"Authorization": f"Bearer {ARCHON_INTERNAL_KEY}"},
                timeout=15.0,
            )
            if status_response.status_code == 200:
                status_payload = status_response.json()
                if status_payload.get("status") in {"COMPLETED", "PARTIAL", "FAILED"}:
                    break
            await asyncio_sleep(3)

        review_response = await client.get(
            f"{ARCHON_API_URL}/api/v1/reviews/{review_id}",
            headers={"Authorization": f"Bearer {ARCHON_INTERNAL_KEY}"},
            timeout=20.0,
        )
        if review_response.status_code != 200:
            return None
        return review_response.json()


async def asyncio_sleep(seconds: int) -> None:
    import asyncio

    await asyncio.sleep(seconds)


async def post_review_comment(installation_id: int, repo_full_name: str, pr_number: int, body: str) -> None:
    token = await get_installation_token(installation_id)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments",
            json={"body": body},
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=30.0,
        )
        response.raise_for_status()


async def post_review_comment_with_retry(
    installation_id: int,
    repo_full_name: str,
    pr_number: int,
    body: str,
) -> bool:
    backoffs = [1, 2, 4]
    for attempt, delay in enumerate(backoffs, start=1):
        try:
            await post_review_comment(installation_id, repo_full_name, pr_number, body)
            return True
        except httpx.HTTPError as exc:
            logger.error("Comment post attempt %s failed for %s#%s: %s", attempt, repo_full_name, pr_number, exc)
            if attempt == len(backoffs):
                return False
            await asyncio_sleep(delay)
    return False


def should_rate_limit(repo_full_name: str, pr_number: int, now: float | None = None) -> bool:
    current = time.monotonic() if now is None else now
    key = (repo_full_name, pr_number)
    last = RECENT_PR_REVIEWS.get(key)
    if last is None:
        return False
    return current - last < REVIEW_RATE_LIMIT_SECONDS


def mark_review_started(repo_full_name: str, pr_number: int, now: float | None = None) -> None:
    RECENT_PR_REVIEWS[(repo_full_name, pr_number)] = time.monotonic() if now is None else now


def build_partial_comment(error: Exception) -> str:
    return (
        "## ARCHON PR Review\n"
        "⚠️ Review partially completed — upstream AI error. Findings so far: none available.\n\n"
        f"Error: {error}"
    )


async def handle_pull_request_event(payload: dict[str, Any]) -> tuple[dict[str, Any], int]:
    event = parse_pr_event(payload)
    if event is None:
        return {"status": "ignored"}, 200

    if should_rate_limit(event.repo_full_name, event.pr_number):
        return {"status": "rate_limited", "detail": "PR reviewed recently"}, 429

    repo_config = await fetch_repo_config(event.installation_id, event.repo_full_name, event.base_branch)
    if event.base_branch not in repo_config.review_branches:
        return {"status": "skipped_branch", "branch": event.base_branch}, 200

    try:
        pr_diff = await fetch_pr_diff(event.installation_id, event.repo_full_name, event.pr_number, repo_config)
        mark_review_started(event.repo_full_name, event.pr_number)
        review_id, job_id = await trigger_pr_review(event, pr_diff)
        review_detail = await wait_for_review_result(review_id, job_id, timeout_seconds=120)
    except (httpx.HTTPError, AnthropicAPIError) as exc:
        logger.error("Upstream AI/review trigger failed for %s#%s: %s", event.repo_full_name, event.pr_number, exc)
        await post_review_comment_with_retry(
            event.installation_id,
            event.repo_full_name,
            event.pr_number,
            build_partial_comment(exc),
        )
        return {"status": "partial_error"}, 200

    if review_detail is None:
        await post_review_comment_with_retry(
            event.installation_id,
            event.repo_full_name,
            event.pr_number,
            "## ARCHON PR Review\n\nReview timed out after 2 minutes. Partial analysis may still complete in ARCHON.",
        )
        return {"status": "timeout", "review_id": review_id}, 200

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
    await post_review_comment_with_retry(event.installation_id, event.repo_full_name, event.pr_number, comment_body)
    return {"status": "review_posted", "review_id": review_id}, 200


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "app": "archon-github-app"}
