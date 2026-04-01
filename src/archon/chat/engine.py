"""Streaming chat engine for architecture Q&A."""
from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator

import anthropic
from sqlalchemy.ext.asyncio import AsyncSession

from archon.config.settings import settings

from .context_builder import build_system_prompt, format_history_for_claude
from .history import get_history, save_message

logger = logging.getLogger(__name__)


async def stream_chat(
    db: AsyncSession,
    review_id: str,
    user_message: str,
) -> AsyncGenerator[str, None]:
    """Stream architecture chat response as SSE-formatted strings.

    Yields lines like: ``data: {"type": "text", "data": "chunk"}\\n\\n``
    Final event:       ``data: {"type": "done", "data": ""}\\n\\n``
    Error event:       ``data: {"type": "error", "data": "message"}\\n\\n``
    """
    # Persist user message first
    await save_message(db, review_id, "user", user_message)

    # Load prior history (everything before this message)
    full_history = await get_history(db, review_id, limit=21)
    prior_history = full_history[:-1]  # exclude the message we just saved

    # Build system prompt with embedded review context
    system_prompt = await build_system_prompt(db, review_id)

    # Build Claude messages array
    messages = format_history_for_claude(prior_history)
    messages.append({"role": "user", "content": user_message})

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    accumulated = ""

    try:
        async with client.messages.stream(
            model=settings.agent_model,
            max_tokens=4096,
            system=system_prompt,
            messages=messages,
        ) as stream:
            async for text in stream.text_stream:
                accumulated += text
                yield f"data: {json.dumps({'type': 'text', 'data': text})}\n\n"

        # Persist full assistant response
        await save_message(db, review_id, "assistant", accumulated)
        yield f"data: {json.dumps({'type': 'done', 'data': ''})}\n\n"

    except anthropic.APIError as exc:
        logger.error("Claude streaming error for review %s: %s", review_id, exc)
        yield f"data: {json.dumps({'type': 'error', 'data': str(exc)})}\n\n"
    except Exception as exc:
        logger.exception("Unexpected error in stream_chat for review %s", review_id)
        yield f"data: {json.dumps({'type': 'error', 'data': 'Internal error — please try again'})}\n\n"
