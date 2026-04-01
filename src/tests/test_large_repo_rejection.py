from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parents[2]))


@pytest.mark.asyncio
async def test_large_repo_rejected_before_agents_invoked() -> None:
    with (
        patch("src.api.workers.review_worker.GitHubReader") as mock_gh_cls,
        patch("src.api.workers.review_worker.InMemoryVectorStore"),
        patch("src.api.workers.review_worker.RAGIndexer") as mock_indexer_cls,
        patch("src.api.workers.review_worker.RAGRetriever"),
        patch("src.api.workers.review_worker.ClaudeAdapter"),
        patch("src.api.workers.review_worker.TavilyAdapter"),
        patch("src.api.workers.review_worker.ExaAdapter"),
        patch("src.api.workers.review_worker.Supervisor") as mock_supervisor_cls,
        patch("src.api.workers.review_worker.update_review_status", new_callable=AsyncMock) as mock_update_review,
        patch("src.api.workers.review_worker.update_job_progress", new_callable=AsyncMock) as mock_update_job,
        patch("src.api.workers.review_worker.settings") as mock_settings,
    ):
        mock_settings.max_loc = 500_000
        mock_settings.embedding_model = "text-embedding-ada-002"

        gh = mock_gh_cls.return_value
        gh.clone = AsyncMock(return_value="/tmp/repo")
        gh.count_loc = AsyncMock(return_value=600_000)
        gh.cleanup = AsyncMock()

        from src.api.workers.review_worker import process_review

        await process_review(
            review_id="rev-oversize",
            job_id="job-oversize",
            repo_url="https://github.com/org/large-repo",
            mode="review",
            user_id="user-1",
        )

        mock_supervisor_cls.assert_not_called()
        mock_indexer_cls.assert_not_called()

        failed_calls = [c for c in mock_update_review.await_args_list if c.args[1] == "FAILED"]
        assert failed_calls
        err = failed_calls[0].kwargs.get("error", "")
        assert "500,000" in err or "too large" in err.lower() or "LOC limit" in err
        assert any(c.args[1] == "FAILED" for c in mock_update_job.await_args_list)
