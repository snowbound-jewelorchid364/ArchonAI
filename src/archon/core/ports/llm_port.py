from __future__ import annotations
from abc import ABC, abstractmethod


class LLMPort(ABC):
    @abstractmethod
    async def complete(
        self,
        system_prompt: str,
        user_message: str,
        *,
        thinking_budget: str | None = None,
        max_tokens: int = 16384,
    ) -> str: ...

    @abstractmethod
    async def complete_structured(
        self,
        system_prompt: str,
        user_message: str,
        response_model: type,
        *,
        thinking_budget: str | None = None,
    ) -> object: ...
