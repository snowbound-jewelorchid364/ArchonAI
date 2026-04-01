"""Tests for Architecture Chat — Phase 6A."""
from __future__ import annotations

import json
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest

from archon.chat.history import ChatMessage


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_review_row(
    review_id: str = "rev-123",
    user_id: str = "user-1",
    status: str = "COMPLETED",
    package_json: dict | None = None,
) -> MagicMock:
    r = MagicMock()
    r.id = review_id
    r.user_id = user_id
    r.repo_url = "https://github.com/org/repo"
    r.mode = "review"
    r.status = status
    r.executive_summary = "The system has several critical security gaps."
    r.package_json = package_json
    return r


def _make_package_json() -> dict:
    return {
        "run_id": "run-1",
        "repo_url": "https://github.com/org/repo",
        "mode": "review",
        "created_at": "2026-04-01T10:00:00Z",
        "duration_seconds": 120.0,
        "executive_summary": "Critical auth issues found.",
        "findings": [
            {
                "id": "f-1",
                "title": "Hardcoded JWT secret",
                "description": "JWT secret is hardcoded in auth.py line 47.",
                "severity": "CRITICAL",
                "domain": "security",
                "file_path": "services/auth/jwt.py",
                "line_number": 47,
                "recommendation": "Move secret to AWS Secrets Manager.",
                "citations": [],
                "confidence": 0.95,
                "from_codebase": True,
            },
            {
                "id": "f-2",
                "title": "Missing rate limiting",
                "description": "No rate limiting on public endpoints.",
                "severity": "HIGH",
                "domain": "software",
                "file_path": None,
                "line_number": None,
                "recommendation": "Add rate limiting middleware.",
                "citations": [],
                "confidence": 0.85,
                "from_codebase": False,
            },
        ],
        "artifacts": [],
        "citations": [],
        "agent_statuses": {},
        "partial": False,
        "model_version": "",
        "prompt_version": "",
    }


def _make_db(review_row: MagicMock | None = None) -> AsyncMock:
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = review_row
    db.execute = AsyncMock(return_value=result)
    db.add = MagicMock()
    db.flush = AsyncMock()
    return db


# ---------------------------------------------------------------------------
# history.py tests
# ---------------------------------------------------------------------------

class TestChatHistory:
    @pytest.mark.asyncio
    async def test_save_message_persists_to_db(self):
        from archon.chat.history import save_message

        db = _make_db()
        msg_row = MagicMock()
        msg_row.id = "msg-1"
        msg_row.review_id = "rev-123"
        msg_row.role = "user"
        msg_row.content = "What are the critical findings?"
        msg_row.citations = []
        msg_row.created_at = datetime.now(UTC)

        with patch("archon.chat.history.ChatMessageRow", return_value=msg_row):
            result = await save_message(db, "rev-123", "user", "What are the critical findings?")

        db.add.assert_called_once()
        db.flush.assert_called_once()
        assert result.role == "user"
        assert result.content == "What are the critical findings?"

    @pytest.mark.asyncio
    async def test_get_history_returns_chronological_order(self):
        from archon.chat.history import get_history

        now = datetime.now(UTC)
        rows = [
            MagicMock(id="m-2", review_id="rev-1", role="assistant", content="Here are the findings...", citations=[], created_at=now),
            MagicMock(id="m-1", review_id="rev-1", role="user", content="What issues?", citations=[], created_at=now),
        ]
        # DB returns descending order (latest first) — history() reverses to chronological
        db = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = rows
        db.execute = AsyncMock(return_value=result_mock)

        history = await get_history(db, "rev-1")

        # Should be reversed to chronological
        assert history[0].id == "m-1"
        assert history[1].id == "m-2"

    @pytest.mark.asyncio
    async def test_get_history_empty_returns_empty_list(self):
        from archon.chat.history import get_history

        db = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        db.execute = AsyncMock(return_value=result_mock)

        history = await get_history(db, "rev-missing")

        assert history == []


# ---------------------------------------------------------------------------
# context_builder.py tests
# ---------------------------------------------------------------------------

class TestContextBuilder:
    @pytest.mark.asyncio
    async def test_system_prompt_includes_findings(self):
        from archon.chat.context_builder import build_system_prompt

        review = _make_review_row(package_json=_make_package_json())
        db = _make_db(review_row=review)

        prompt = await build_system_prompt(db, "rev-123")

        assert "Hardcoded JWT secret" in prompt
        assert "CRITICAL" in prompt
        assert "security" in prompt
        assert "services/auth/jwt.py" in prompt

    @pytest.mark.asyncio
    async def test_system_prompt_includes_executive_summary(self):
        from archon.chat.context_builder import build_system_prompt

        review = _make_review_row(package_json=_make_package_json())
        db = _make_db(review_row=review)

        prompt = await build_system_prompt(db, "rev-123")

        assert "Critical auth issues found." in prompt

    @pytest.mark.asyncio
    async def test_system_prompt_no_review(self):
        from archon.chat.context_builder import build_system_prompt

        db = _make_db(review_row=None)
        prompt = await build_system_prompt(db, "rev-missing")

        assert "No review found" in prompt

    @pytest.mark.asyncio
    async def test_system_prompt_running_review(self):
        from archon.chat.context_builder import build_system_prompt

        review = _make_review_row(status="RUNNING", package_json=None)
        db = _make_db(review_row=review)

        prompt = await build_system_prompt(db, "rev-running")

        assert "still running" in prompt

    def test_format_history_for_claude(self):
        from archon.chat.context_builder import format_history_for_claude

        history = [
            ChatMessage(id="1", review_id="r", role="user", content="Hello"),
            ChatMessage(id="2", review_id="r", role="assistant", content="Hi there"),
        ]
        result = format_history_for_claude(history)

        assert result == [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]


# ---------------------------------------------------------------------------
# engine.py tests
# ---------------------------------------------------------------------------

class TestChatEngine:
    @pytest.mark.asyncio
    async def test_stream_chat_yields_text_and_done_events(self):
        from archon.chat.engine import stream_chat

        review = _make_review_row(package_json=_make_package_json())
        db = _make_db(review_row=review)

        # Mock save_message and get_history
        mock_history = []
        mock_user_msg = ChatMessage(id="u-1", review_id="rev-123", role="user", content="What are the critical issues?")
        mock_assist_msg = ChatMessage(id="a-1", review_id="rev-123", role="assistant", content="The critical issue is...")

        async def mock_text_stream():
            for chunk in ["The critical ", "issue is..."]:
                yield chunk

        mock_stream_ctx = AsyncMock()
        mock_stream_ctx.__aenter__ = AsyncMock(return_value=mock_stream_ctx)
        mock_stream_ctx.__aexit__ = AsyncMock(return_value=False)
        mock_stream_ctx.text_stream = mock_text_stream()

        with (
            patch("archon.chat.engine.save_message", side_effect=[mock_user_msg, mock_assist_msg]) as mock_save,
            patch("archon.chat.engine.get_history", return_value=[mock_user_msg]),
            patch("archon.chat.engine.build_system_prompt", return_value="System prompt"),
            patch("archon.chat.engine.anthropic.AsyncAnthropic") as mock_anthropic,
        ):
            mock_anthropic.return_value.messages.stream.return_value = mock_stream_ctx

            events = []
            async for event in stream_chat(db, "rev-123", "What are the critical issues?"):
                events.append(json.loads(event[len("data: "):]))

        text_events = [e for e in events if e["type"] == "text"]
        done_events = [e for e in events if e["type"] == "done"]

        assert len(text_events) == 2
        assert text_events[0]["data"] == "The critical "
        assert text_events[1]["data"] == "issue is..."
        assert len(done_events) == 1
        # User message + assistant message both saved
        assert mock_save.call_count == 2

    @pytest.mark.asyncio
    async def test_stream_chat_yields_error_on_api_failure(self):
        import anthropic as anthropic_lib
        from archon.chat.engine import stream_chat

        review = _make_review_row(package_json=_make_package_json())
        db = _make_db(review_row=review)

        mock_user_msg = ChatMessage(id="u-1", review_id="rev-123", role="user", content="Hello")

        mock_stream_ctx = AsyncMock()
        mock_stream_ctx.__aenter__ = AsyncMock(side_effect=anthropic_lib.APIError(
            message="rate limit", request=MagicMock(), body={}
        ))
        mock_stream_ctx.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("archon.chat.engine.save_message", return_value=mock_user_msg),
            patch("archon.chat.engine.get_history", return_value=[]),
            patch("archon.chat.engine.build_system_prompt", return_value="System"),
            patch("archon.chat.engine.anthropic.AsyncAnthropic") as mock_anthropic,
        ):
            mock_anthropic.return_value.messages.stream.return_value = mock_stream_ctx

            events = []
            async for event in stream_chat(db, "rev-123", "Hello"):
                events.append(json.loads(event[len("data: "):]))

        error_events = [e for e in events if e["type"] == "error"]
        assert len(error_events) == 1
