from __future__ import annotations
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


_FAKE_RESPONSE_TEXT = (
    "Components: API Gateway, Lambda, DynamoDB. "
    "Data flows from client to gateway to Lambda. "
    "Cloud provider: AWS."
)


def _make_mock_anthropic():
    mock_block = MagicMock()
    mock_block.text = _FAKE_RESPONSE_TEXT

    mock_message = MagicMock()
    mock_message.content = [mock_block]

    mock_messages = AsyncMock()
    mock_messages.create = AsyncMock(return_value=mock_message)

    mock_client = MagicMock()
    mock_client.messages = mock_messages
    return mock_client


@pytest.mark.asyncio
async def test_image_parser_calls_claude_vision():
    from archon.input.image_parser import ImageParser
    fake_image_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100  # minimal fake PNG

    mock_client = _make_mock_anthropic()
    with patch("archon.input.image_parser.anthropic.AsyncAnthropic", return_value=mock_client):
        await ImageParser().parse(fake_image_bytes)

    mock_client.messages.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_image_parser_returns_description():
    from archon.input.image_parser import ImageParser
    fake_image_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

    mock_client = _make_mock_anthropic()
    with patch("archon.input.image_parser.anthropic.AsyncAnthropic", return_value=mock_client):
        parsed = await ImageParser().parse(fake_image_bytes)

    assert parsed.content == _FAKE_RESPONSE_TEXT
    assert parsed.source_type == "image"
