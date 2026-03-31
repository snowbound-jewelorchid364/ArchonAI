from __future__ import annotations
import json
import logging
import anthropic
from ...core.ports.llm_port import LLMPort
from ...config.settings import settings

logger = logging.getLogger(__name__)


class ClaudeAdapter(LLMPort):
    def __init__(self, model: str | None = None) -> None:
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._model = model or settings.agent_model

    async def complete(
        self,
        system_prompt: str,
        user_message: str,
        *,
        thinking_budget: str | None = None,
        max_tokens: int = 16384,
    ) -> str:
        budget = thinking_budget or settings.thinking_budget_default
        budget_tokens = {"low": 1024, "medium": 8192, "high": 32768}
        thinking_tokens = budget_tokens.get(budget, 8192)

        try:
            message = await self._client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                thinking={
                    "type": "enabled",
                    "budget_tokens": thinking_tokens,
                },
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            # Extract text from response (thinking blocks are separate)
            text_parts = [
                block.text for block in message.content
                if hasattr(block, "text")
            ]
            return "\n".join(text_parts)
        except anthropic.APIError as exc:
            logger.warning("Claude API error (thinking=%s): %s — falling back to standard", budget, exc)
            # Fallback: retry without extended thinking
            message = await self._client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            return message.content[0].text

    async def complete_structured(
        self,
        system_prompt: str,
        user_message: str,
        response_model: type,
        *,
        thinking_budget: str | None = None,
    ) -> object:
        raw = await self.complete(
            system_prompt=system_prompt + "\n\nRespond with valid JSON only. No markdown fences.",
            user_message=user_message,
            thinking_budget=thinking_budget or "low",
        )
        # Strip markdown fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        return response_model.model_validate(json.loads(cleaned))
