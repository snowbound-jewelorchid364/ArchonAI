"""Tests for the share backend — worker token generation and GET endpoint response shape."""
from __future__ import annotations
from datetime import datetime, timedelta, UTC
from unittest.mock import AsyncMock, MagicMock, patch
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_review(
    pkg_json: dict | None = None,
    status: str = "COMPLETED",
    user_id: str = "user-123",
    review_id: str = "rev-abc",
) -> MagicMock:
    r = MagicMock()
    r.id = review_id
    r.user_id = user_id
    r.repo_url = "https://github.com/org/repo"
    r.mode = "review"
    r.status = status
    r.partial = False
    r.finding_count = 2
    r.critical_count = 1
    r.high_count = 1
    r.confidence = 0.85
    r.duration_seconds = 42.0
    r.executive_summary = "Summary text"
    r.agent_statuses = {}
    r.package_json = pkg_json
    r.created_at = datetime(2025, 1, 1, tzinfo=UTC)
    return r


def _make_link(
    token: str = "tok123",
    review_id: str = "rev-abc",
    user_id: str = "user-123",
    is_active: bool = True,
    expires_at: datetime | None = None,
) -> MagicMock:
    lk = MagicMock()
    lk.token = token
    lk.review_id = review_id
    lk.user_id = user_id
    lk.is_active = is_active
    lk.expires_at = expires_at
    return lk


def _make_package():
    from src.archon.core.models.review_package import ReviewPackage
    return ReviewPackage(
        run_id="r1",
        repo_url="https://github.com/org/repo",
        mode="review",
        duration_seconds=0.0,
        executive_summary="",
        findings=[],
        artifacts=[],
        citations=[],
        agent_statuses={},
    )


def _make_session(link=None, review=None) -> AsyncMock:
    sess = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = link
    sess.execute = AsyncMock(return_value=result_mock)
    sess.get = AsyncMock(return_value=review)
    return sess


# ---------------------------------------------------------------------------
# Worker: share token auto-generation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_process_review_sets_share_token_on_package():
    """After a successful run, package.share_token must be set."""
    fake_pkg = _make_package()

    with (
        patch("src.api.workers.review_worker.GitHubReader") as mock_gh_cls,
        patch("src.api.workers.review_worker.InMemoryVectorStore"),
        patch("src.api.workers.review_worker.RAGIndexer") as mock_idx_cls,
        patch("src.api.workers.review_worker.RAGRetriever"),
        patch("src.api.workers.review_worker.ClaudeAdapter"),
        patch("src.api.workers.review_worker.TavilyAdapter"),
        patch("src.api.workers.review_worker.ExaAdapter"),
        patch("src.api.workers.review_worker.Supervisor") as mock_sup_cls,
        patch("src.api.workers.review_worker.update_review_status", new_callable=AsyncMock),
        patch("src.api.workers.review_worker.update_job_progress", new_callable=AsyncMock),
        patch("src.api.workers.review_worker.get_session") as mock_sess,
        patch("src.api.workers.review_worker.settings") as mock_settings,
    ):
        mock_settings.max_loc = 500_000
        mock_settings.embedding_model = "text-embedding-ada-002"

        gh = mock_gh_cls.return_value
        gh.clone = AsyncMock(return_value="/tmp/repo")
        gh.count_loc = AsyncMock(return_value=1000)
        gh.cleanup = AsyncMock()

        mock_idx_cls.return_value.index = AsyncMock(return_value=50)
        mock_sup_cls.return_value.run = AsyncMock(return_value=fake_pkg)

        # Simulate async with get_session() as session
        inner_sess = MagicMock()
        inner_sess.add = MagicMock()
        inner_sess.commit = AsyncMock()
        mock_sess.return_value.__aenter__ = AsyncMock(return_value=inner_sess)
        mock_sess.return_value.__aexit__ = AsyncMock(return_value=False)

        from src.api.workers.review_worker import process_review
        await process_review(
            review_id="rev-1", job_id="job-1",
            repo_url="https://github.com/org/repo", mode="review",
            user_id="user-123",
        )

    assert fake_pkg.share_token is not None
    assert len(fake_pkg.share_token) > 10


@pytest.mark.asyncio
async def test_process_review_skips_db_insert_when_no_user_id():
    """When user_id is empty string, worker skips ShareLinkRow insert but still sets share_token."""
    fake_pkg = _make_package()

    with (
        patch("src.api.workers.review_worker.GitHubReader") as mock_gh_cls,
        patch("src.api.workers.review_worker.InMemoryVectorStore"),
        patch("src.api.workers.review_worker.RAGIndexer") as mock_idx_cls,
        patch("src.api.workers.review_worker.RAGRetriever"),
        patch("src.api.workers.review_worker.ClaudeAdapter"),
        patch("src.api.workers.review_worker.TavilyAdapter"),
        patch("src.api.workers.review_worker.ExaAdapter"),
        patch("src.api.workers.review_worker.Supervisor") as mock_sup_cls,
        patch("src.api.workers.review_worker.update_review_status", new_callable=AsyncMock),
        patch("src.api.workers.review_worker.update_job_progress", new_callable=AsyncMock),
        patch("src.api.workers.review_worker.get_session") as mock_sess,
        patch("src.api.workers.review_worker.settings") as mock_settings,
    ):
        mock_settings.max_loc = 500_000
        mock_settings.embedding_model = "text-embedding-ada-002"

        gh = mock_gh_cls.return_value
        gh.clone = AsyncMock(return_value="/tmp/repo")
        gh.count_loc = AsyncMock(return_value=1000)
        gh.cleanup = AsyncMock()

        mock_idx_cls.return_value.index = AsyncMock(return_value=50)
        mock_sup_cls.return_value.run = AsyncMock(return_value=fake_pkg)

        from src.api.workers.review_worker import process_review
        await process_review(
            review_id="rev-1", job_id="job-1",
            repo_url="https://github.com/org/repo", mode="review",
            user_id="",  # no user_id — should skip DB insert
        )

    # get_session should NOT have been called
    mock_sess.assert_not_called()
    assert fake_pkg.share_token is not None


# ---------------------------------------------------------------------------
# share.py GET endpoint — call route function directly (bypasses FastAPI DI)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_shared_review_returns_flat_findings():
    """GET /share/{token} must return findings at top level, not nested in package_json."""
    from src.api.routes.share import get_shared_review

    pkg_json = {
        "run_id": "run-xyz",
        "findings": [{"id": "f1", "title": "Test finding", "severity": "HIGH"}],
        "artifacts": [],
        "citations": [],
        "agent_statuses": {"sw": "COMPLETED"},
        "executive_summary": "All good.",
        "partial": False,
        "duration_seconds": 10.5,
        "confidence": 0.9,
    }
    session = _make_session(link=_make_link(), review=_make_review(pkg_json=pkg_json))

    data = await get_shared_review(token="tok123", session=session)

    assert "findings" in data
    assert "package_json" not in data
    assert data["findings"] == pkg_json["findings"]
    assert data["run_id"] == "run-xyz"
    assert data["share_token"] == "tok123"
    assert data["executive_summary"] == "All good."


@pytest.mark.asyncio
async def test_get_shared_review_expired_raises_410():
    """Expired share links must raise HTTP 410."""
    from fastapi import HTTPException
    from src.api.routes.share import get_shared_review

    expired_link = _make_link(expires_at=datetime(2020, 1, 1, tzinfo=UTC))
    session = _make_session(link=expired_link)

    with pytest.raises(HTTPException) as exc_info:
        await get_shared_review(token="tok-expired", session=session)

    assert exc_info.value.status_code == 410


@pytest.mark.asyncio
async def test_get_shared_review_falls_back_when_no_package_json():
    """If package_json is None, review-row fields are used as fallback."""
    from src.api.routes.share import get_shared_review

    review = _make_review(pkg_json=None)
    session = _make_session(link=_make_link(), review=review)

    data = await get_shared_review(token="tok123", session=session)

    assert data["findings"] == []
    assert data["artifacts"] == []
    assert data["executive_summary"] == "Summary text"
    assert data["run_id"] == "rev-abc"
    assert data["share_token"] == "tok123"
