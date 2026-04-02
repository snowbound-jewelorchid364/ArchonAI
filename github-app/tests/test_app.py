from __future__ import annotations

import hashlib
import hmac
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

for module_name in ['src', 'src.app', 'src.callback', 'src.repo_config']:
    sys.modules.pop(module_name, None)

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))
sys.path.append(str(Path(__file__).parents[2] / "src"))

from src.app import AnthropicAPIError, RECENT_PR_REVIEWS, app, post_review_comment_with_retry
import src.app as github_app


def _signature(secret: str, payload: bytes) -> str:
    digest = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def _payload(base_branch: str = "main") -> dict:
    return {
        "action": "opened",
        "pull_request": {
            "number": 7,
            "title": "Refactor auth",
            "head": {"ref": "feature/auth"},
            "base": {"ref": base_branch},
        },
        "repository": {"full_name": "o/r", "html_url": "https://github.com/o/r"},
        "installation": {"id": 123},
    }


@pytest.fixture(autouse=True)
def clear_rate_limit() -> None:
    RECENT_PR_REVIEWS.clear()


@pytest.mark.asyncio
async def test_webhook_signature_valid(monkeypatch) -> None:
    payload = _payload()
    body = json.dumps(payload).encode()
    monkeypatch.setattr(github_app, "GITHUB_WEBHOOK_SECRET", "secret")
    monkeypatch.setattr(github_app, "handle_pull_request_event", AsyncMock(return_value=({"status": "ok"}, 200)))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/webhooks/github",
            content=body,
            headers={
                "X-Hub-Signature-256": _signature("secret", body),
                "X-GitHub-Event": "pull_request",
                "Content-Type": "application/json",
            },
        )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_webhook_signature_invalid(monkeypatch) -> None:
    payload = _payload()
    body = json.dumps(payload).encode()
    monkeypatch.setattr(github_app, "GITHUB_WEBHOOK_SECRET", "secret")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/webhooks/github",
            content=body,
            headers={
                "X-Hub-Signature-256": "sha256=bad",
                "X-GitHub-Event": "pull_request",
                "Content-Type": "application/json",
            },
        )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_wrong_branch_skipped(monkeypatch) -> None:
    repo_config = MagicMock()
    repo_config.review_branches = ["develop"]
    repo_config.ignore_patterns = []
    repo_config.max_files = 100
    monkeypatch.setattr(github_app, "fetch_repo_config", AsyncMock(return_value=repo_config))
    monkeypatch.setattr(github_app, "fetch_pr_diff", AsyncMock())
    payload = _payload(base_branch="main")
    body = json.dumps(payload).encode()
    monkeypatch.setattr(github_app, "GITHUB_WEBHOOK_SECRET", "secret")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/webhooks/github",
            content=body,
            headers={
                "X-Hub-Signature-256": _signature("secret", body),
                "X-GitHub-Event": "pull_request",
                "Content-Type": "application/json",
            },
        )

    assert response.status_code == 200
    assert response.json()["status"] == "skipped_branch"
    github_app.fetch_pr_diff.assert_not_called()


@pytest.mark.asyncio
async def test_rate_limit_blocks_second_review(monkeypatch) -> None:
    payload = _payload()
    body = json.dumps(payload).encode()
    monkeypatch.setattr(github_app, "GITHUB_WEBHOOK_SECRET", "secret")

    repo_config = MagicMock()
    repo_config.review_branches = ["main"]
    repo_config.ignore_patterns = []
    repo_config.max_files = 100
    monkeypatch.setattr(github_app, "fetch_repo_config", AsyncMock(return_value=repo_config))
    monkeypatch.setattr(github_app, "fetch_pr_diff", AsyncMock(return_value="diff"))
    monkeypatch.setattr(github_app, "trigger_pr_review", AsyncMock(return_value=("r1", "j1")))
    monkeypatch.setattr(github_app, "wait_for_review_result", AsyncMock(return_value={"agent_statuses": {}, "executive_summary": "ok", "partial": False, "duration_seconds": 1}))
    monkeypatch.setattr(github_app, "post_review_comment_with_retry", AsyncMock(return_value=True))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        first = await client.post(
            "/webhooks/github",
            content=body,
            headers={
                "X-Hub-Signature-256": _signature("secret", body),
                "X-GitHub-Event": "pull_request",
                "Content-Type": "application/json",
            },
        )
        second = await client.post(
            "/webhooks/github",
            content=body,
            headers={
                "X-Hub-Signature-256": _signature("secret", body),
                "X-GitHub-Event": "pull_request",
                "Content-Type": "application/json",
            },
        )

    assert first.status_code == 200
    assert second.status_code == 429


@pytest.mark.asyncio
async def test_anthropic_failure_posts_partial_comment(monkeypatch) -> None:
    payload = _payload()
    body = json.dumps(payload).encode()
    monkeypatch.setattr(github_app, "GITHUB_WEBHOOK_SECRET", "secret")

    repo_config = MagicMock()
    repo_config.review_branches = ["main"]
    repo_config.ignore_patterns = []
    repo_config.max_files = 100
    monkeypatch.setattr(github_app, "fetch_repo_config", AsyncMock(return_value=repo_config))
    monkeypatch.setattr(github_app, "fetch_pr_diff", AsyncMock(return_value="diff"))
    monkeypatch.setattr(github_app, "trigger_pr_review", AsyncMock(side_effect=AnthropicAPIError("boom", request=MagicMock(), body=None)))
    posted: list[str] = []

    async def fake_post(*args, **kwargs):
        posted.append(kwargs["body"] if "body" in kwargs else args[3])
        return True

    monkeypatch.setattr(github_app, "post_review_comment_with_retry", fake_post)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/webhooks/github",
            content=body,
            headers={
                "X-Hub-Signature-256": _signature("secret", body),
                "X-GitHub-Event": "pull_request",
                "Content-Type": "application/json",
            },
        )

    assert response.status_code == 200
    assert response.json()["status"] == "partial_error"
    assert posted and "upstream AI error" in posted[0]


@pytest.mark.asyncio
async def test_retry_on_comment_failure(monkeypatch) -> None:
    calls = {"count": 0}

    async def flaky_post(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] < 3:
            raise httpx.HTTPError("boom")

    monkeypatch.setattr(github_app, "post_review_comment", flaky_post)
    monkeypatch.setattr(github_app, "asyncio_sleep", AsyncMock(return_value=None))

    ok = await post_review_comment_with_retry(1, "o/r", 7, "hello")

    assert ok is True
    assert calls["count"] == 3




