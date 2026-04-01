"""Tests for ClaudeAdapter — thinking budgets, fallback, retry."""
from __future__ import annotations
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import anthropic


@pytest.fixture
def adapter():
    with patch("archon.infrastructure.llm.claude_adapter.settings") as mock_settings:
        mock_settings.anthropic_api_key = "test-key"
        mock_settings.agent_model = "claude-opus-4-5"
        mock_settings.thinking_budget_default = "medium"
        from archon.infrastructure.llm.claude_adapter import ClaudeAdapter
        a = ClaudeAdapter.__new__(ClaudeAdapter)
        a._client = AsyncMock()
        a._model = "claude-opus-4-5"
        return a


def _make_response(text: str):
    block = MagicMock()
    block.text = text
    msg = MagicMock()
    msg.content = [block]
    return msg


@pytest.mark.asyncio
async def test_low_thinking_budget(adapter):
    """Low budget uses 1024 thinking tokens."""
    adapter._client.messages.create = AsyncMock(return_value=_make_response("result"))
    result = await adapter.complete("system", "user", thinking_budget="low")
    assert result == "result"
    call_kwargs = adapter._client.messages.create.call_args[1]
    assert call_kwargs["thinking"]["budget_tokens"] == 1024


@pytest.mark.asyncio
async def test_medium_thinking_budget(adapter):
    """Medium budget uses 8192 thinking tokens."""
    adapter._client.messages.create = AsyncMock(return_value=_make_response("result"))
    await adapter.complete("system", "user", thinking_budget="medium")
    call_kwargs = adapter._client.messages.create.call_args[1]
    assert call_kwargs["thinking"]["budget_tokens"] == 8192


@pytest.mark.asyncio
async def test_high_thinking_budget(adapter):
    """High budget uses 32768 thinking tokens."""
    adapter._client.messages.create = AsyncMock(return_value=_make_response("result"))
    await adapter.complete("system", "user", thinking_budget="high")
    call_kwargs = adapter._client.messages.create.call_args[1]
    assert call_kwargs["thinking"]["budget_tokens"] == 32768


@pytest.mark.asyncio
async def test_fallback_on_api_error(adapter):
    """On APIError with thinking, falls back to standard mode."""
    error_response = MagicMock()
    error_response.status_code = 400
    api_error = anthropic.APIError(
        message="thinking not supported",
        request=MagicMock(),
        body=None,
    )
    adapter._client.messages.create = AsyncMock(
        side_effect=[api_error, _make_response("fallback result")]
    )
    result = await adapter.complete("system", "user", thinking_budget="high")
    assert result == "fallback result"
    assert adapter._client.messages.create.call_count == 2
    fallback_kwargs = adapter._client.messages.create.call_args_list[1][1]
    assert "thinking" not in fallback_kwargs


@pytest.mark.asyncio
async def test_complete_structured(adapter):
    """complete_structured parses JSON response into a Pydantic model."""
    from pydantic import BaseModel
    class TestModel(BaseModel):
        name: str
        value: int
    adapter._client.messages.create = AsyncMock(
        return_value=_make_response('{"name": "test", "value": 42}')
    )
    result = await adapter.complete_structured("system", "user", TestModel)
    assert result.name == "test"
    assert result.value == 42
