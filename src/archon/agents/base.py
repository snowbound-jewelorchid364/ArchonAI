from __future__ import annotations
import asyncio
import time
import logging
from abc import ABC, abstractmethod
from ..core.models import AgentOutput
from ..core.ports.llm_port import LLMPort
from ..core.ports.search_port import SearchPort
from ..rag.retriever import RAGRetriever
from ..config.settings import settings

logger = logging.getLogger(__name__)


class BaseArchitectAgent(ABC):
    domain: str = ""
    _prompt_path: str = ""

    def __init__(self, llm: LLMPort, searchers: list[SearchPort], retriever: RAGRetriever) -> None:
        self._llm = llm
        self._searchers = searchers
        self._retriever = retriever
        self._system_prompt = self._load_prompt()

    def _load_prompt(self) -> str:
        from pathlib import Path
        path = Path(__file__).parents[3] / "prompts" / self._prompt_path
        if path.exists():
            return path.read_text(encoding="utf-8")
        return f"You are ARCHON's {self.domain} specialist architect."

    async def _search(self, query: str, max_results: int = 5) -> list:
        results = []
        for searcher in self._searchers:
            try:
                found = await searcher.search(query, max_results=max_results)
                results.extend(found)
            except Exception as exc:
                logger.warning("Search failed for %s: %s", self.domain, exc)
        return results

    async def _retrieve_context(self, query: str) -> str:
        return await self._retriever.retrieve_as_context(query)

    @abstractmethod
    async def _analyse(self, repo_context: str, mode: str, mode_focus: str = "") -> AgentOutput: ...

    async def run(self, mode: str, *, mode_focus: str = "") -> AgentOutput:
        start = time.monotonic()
        try:
            context = await self._retrieve_context(f"{self.domain} architecture patterns issues")
            output = await asyncio.wait_for(
                self._analyse(context, mode, mode_focus=mode_focus),
                timeout=settings.agent_timeout_seconds,
            )
            output.duration_seconds = time.monotonic() - start
            return output
        except asyncio.TimeoutError:
            logger.error("Agent %s timed out", self.domain)
            return AgentOutput(
                domain=self.domain, confidence=0.0,
                duration_seconds=time.monotonic() - start,
                error="Agent timed out", partial=True,
            )
        except Exception as exc:
            logger.exception("Agent %s failed: %s", self.domain, exc)
            return AgentOutput(
                domain=self.domain, confidence=0.0,
                duration_seconds=time.monotonic() - start,
                error=str(exc), partial=True,
            )
