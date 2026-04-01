"""Tests for all API routes (B3 blocker).

Tests health, reviews, jobs, packages, feedback, webhooks.
Share, billing, and history routes use DB sessions directly — tested with mocked deps.
"""
from __future__ import annotations

import json
import pytest
import pytest_asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Minimal app factory that avoids lifespan DB init
# ---------------------------------------------------------------------------

def _make_test_app() -> FastAPI:
    """Build a test app with auth dependency overridden."""
    from api.main import create_app
    from api.dependencies import require_user, get_current_user, get_db
    from api.schemas.auth import CurrentUser

    # Patch lifespan to be a no-op
    from contextlib import asynccontextmanager
    @asynccontextmanager
    async def noop_lifespan(app):
        yield

    app = FastAPI(lifespan=noop_lifespan)

    # Copy routers from the real app factory
    from api.routes import health, reviews, jobs, packages, webhooks, feedback
    app.include_router(health.router)
    app.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
    app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
    app.include_router(packages.router, prefix="/packages", tags=["packages"])
    app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
    app.include_router(feedback.router, tags=["feedback"])

    test_user = CurrentUser(user_id="test-user-1", email="test@archon.ai", plan="pro")

    async def override_require_user():
        return test_user

    async def override_get_current_user():
        return {"sub": "test-user-1", "email": "test@archon.ai"}

    app.dependency_overrides[require_user] = override_require_user
    app.dependency_overrides[get_current_user] = override_get_current_user

    return app


@pytest.fixture
def client():
    app = _make_test_app()
    return TestClient(app)


# ---- HEALTH ----

def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "archon-api"


# ---- REVIEWS ----

@patch("api.routes.reviews.create_review", new_callable=AsyncMock)
@patch("api.routes.reviews.check_plan_limit", new_callable=AsyncMock)
def test_create_review_success(mock_limit, mock_create, client):
    mock_limit.return_value = (True, "")
    mock_create.return_value = ("rev-123", "job-456")

    resp = client.post("/reviews", json={
        "repo_url": "https://github.com/user/repo",
        "mode": "review",
    })
    assert resp.status_code == 202
    data = resp.json()
    assert data["review_id"] == "rev-123"
    assert data["job_id"] == "job-456"
    assert data["status"] == "QUEUED"


@patch("api.routes.reviews.check_plan_limit", new_callable=AsyncMock)
def test_create_review_invalid_mode(mock_limit, client):
    mock_limit.return_value = (True, "")
    resp = client.post("/reviews", json={
        "repo_url": "https://github.com/user/repo",
        "mode": "invalid_mode",
    })
    assert resp.status_code == 400
    assert "Invalid mode" in resp.json()["detail"]


def test_create_review_non_github_url(client):
    resp = client.post("/reviews", json={
        "repo_url": "https://gitlab.com/user/repo",
        "mode": "review",
    })
    assert resp.status_code == 400
    assert "github.com" in resp.json()["detail"]


@patch("api.routes.reviews.check_plan_limit", new_callable=AsyncMock)
def test_create_review_plan_limit(mock_limit, client):
    mock_limit.return_value = (False, "Monthly review limit reached")
    resp = client.post("/reviews", json={
        "repo_url": "https://github.com/user/repo",
        "mode": "review",
    })
    assert resp.status_code == 402
    assert "limit" in resp.json()["detail"].lower()


@patch("api.routes.reviews.list_reviews", new_callable=AsyncMock)
def test_list_reviews(mock_list, client):
    mock_list.return_value = [
        SimpleNamespace(
            id="rev-1", repo_url="https://github.com/a/b", mode="review",
            status="COMPLETED", finding_count=5, critical_count=1, high_count=2,
            created_at=datetime(2024, 1, 1, tzinfo=timezone.utc), completed_at=None,
        )
    ]
    resp = client.get("/reviews")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == "rev-1"


@patch("api.routes.reviews.get_review", new_callable=AsyncMock)
def test_get_review_not_found(mock_get, client):
    mock_get.return_value = None
    resp = client.get("/reviews/nonexistent")
    assert resp.status_code == 404


# ---- JOBS ----

@patch("api.routes.jobs.get_job", new_callable=AsyncMock)
def test_job_status(mock_job, client):
    mock_job.return_value = SimpleNamespace(
        id="job-1", review_id="rev-1", status="RUNNING", progress={"agents_done": 2}
    )
    resp = client.get("/jobs/job-1/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "RUNNING"
    assert data["progress"]["agents_done"] == 2


@patch("api.routes.jobs.get_job", new_callable=AsyncMock)
def test_job_status_not_found(mock_job, client):
    mock_job.return_value = None
    resp = client.get("/jobs/nonexistent/status")
    assert resp.status_code == 404


# ---- PACKAGES ----

@patch("api.routes.packages.get_review", new_callable=AsyncMock)
def test_download_not_ready(mock_get, client):
    mock_get.return_value = SimpleNamespace(
        status="RUNNING", package_json=None, executive_summary=None
    )
    resp = client.get("/packages/rev-1/download")
    assert resp.status_code == 400
    assert "not ready" in resp.json()["detail"].lower()


@patch("api.routes.packages.get_review", new_callable=AsyncMock)
def test_download_not_found(mock_get, client):
    mock_get.return_value = None
    resp = client.get("/packages/rev-1/download")
    assert resp.status_code == 404


@patch("api.routes.packages.get_review", new_callable=AsyncMock)
def test_download_success(mock_get, client):
    mock_get.return_value = SimpleNamespace(
        status="COMPLETED",
        executive_summary="Test summary",
        agent_statuses={},
        package_json={
            "findings": [
                {"domain": "security", "severity": "HIGH", "title": "SQL Injection",
                 "description": "Found SQLi", "file_path": "app.py", "recommendation": "Use params",
                 "confidence": 0.9},
            ],
            "adrs": [],
            "citations": [],
        },
    )
    resp = client.get("/packages/rev-1/download")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"


# ---- FEEDBACK ----

def test_submit_feedback(client):
    resp = client.post("/reviews/rev-1/feedback", json={
        "finding_id": "f-1",
        "helpful": True,
        "comment": "Great finding!",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["helpful"] is True
    assert data["finding_id"] == "f-1"


def test_get_feedback_summary(client):
    # Submit one first
    client.post("/reviews/rev-2/feedback", json={
        "finding_id": "f-1", "helpful": True, "comment": "Useful",
    })
    client.post("/reviews/rev-2/feedback", json={
        "finding_id": "f-2", "helpful": False, "comment": "",
    })
    resp = client.get("/reviews/rev-2/feedback")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert data["helpful_count"] == 1
    assert data["unhelpful_count"] == 1


# ---- WEBHOOKS ----

def test_github_webhook_ping(client):
    resp = client.post(
        "/webhooks/github",
        json={"zen": "Non-blocking is better than blocking."},
        headers={"X-GitHub-Event": "ping"},
    )
    assert resp.status_code == 200


def test_github_webhook_pr_opened(client):
    resp = client.post(
        "/webhooks/github",
        json={
            "action": "opened",
            "pull_request": {"number": 42},
            "repository": {"html_url": "https://github.com/user/repo"},
        },
        headers={"X-GitHub-Event": "pull_request"},
    )
    assert resp.status_code == 202
    assert "42" in resp.json()["message"]
