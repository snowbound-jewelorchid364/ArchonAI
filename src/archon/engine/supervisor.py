from __future__ import annotations
import asyncio
import logging
import time
import uuid
from ..agents import (
    SoftwareArchitectAgent, CloudArchitectAgent, SecurityArchitectAgent,
    DataArchitectAgent, IntegrationArchitectAgent, AiArchitectAgent,
)
from ..core.models import AgentOutput, ReviewPackage, Finding
from ..core.ports.llm_port import LLMPort
from ..core.ports.search_port import SearchPort
from ..rag.retriever import RAGRetriever
from ..config.settings import settings
from .hitl.checkpoints import HITLMode, CheckpointType
from .hitl.session import HITLSession

logger = logging.getLogger(__name__)


class Supervisor:
    def __init__(self, llm: LLMPort, searchers: list[SearchPort], retriever: RAGRetriever) -> None:
        self._agents = [
            SoftwareArchitectAgent(llm, searchers, retriever),
            CloudArchitectAgent(llm, searchers, retriever),
            SecurityArchitectAgent(llm, searchers, retriever),
            DataArchitectAgent(llm, searchers, retriever),
            IntegrationArchitectAgent(llm, searchers, retriever),
            AiArchitectAgent(llm, searchers, retriever),
        ]
        self._llm = llm

    async def run(
        self,
        repo_url: str,
        mode: str,
        *,
        job_id: str | None = None,
        hitl_mode: HITLMode = HITLMode.AUTOPILOT,
        on_checkpoint: object = None,
    ) -> ReviewPackage:
        run_id = job_id or str(uuid.uuid4())
        start = time.monotonic()
        thinking_budget = settings.thinking_budget_for_mode(mode)
        session = HITLSession(job_id=run_id, hitl_mode=hitl_mode)

        logger.info(
            "Supervisor starting run %s | mode: %s | thinking: %s | hitl: %s",
            run_id, mode, thinking_budget, hitl_mode.value,
        )

        # --- Checkpoint: AGENTS_STARTED ---
        if session.needs_checkpoint(CheckpointType.AGENTS_STARTED):
            cp = session.record_checkpoint(
                CheckpointType.AGENTS_STARTED,
                {"agents": [a.domain for a in self._agents], "mode": mode},
            )
            if on_checkpoint:
                await on_checkpoint(cp)
            else:
                await session.wait_for_approval(cp)
            logger.info("Checkpoint AGENTS_STARTED approved")

        # Fan out all 6 agents in parallel
        results = await asyncio.gather(
            *[agent.run(mode) for agent in self._agents],
            return_exceptions=True,
        )

        outputs: list[AgentOutput] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                agent_name = self._agents[i].domain
                logger.error("Agent %s raised: %s", agent_name, result)
                outputs.append(AgentOutput(
                    domain=agent_name,
                    confidence=0.0,
                    duration_seconds=0.0,
                    error=str(result),
                    partial=True,
                ))
            else:
                outputs.append(result)

        findings = self._deduplicate(
            [f for o in outputs for f in o.findings]
        )
        citations = list({c.url: c for o in outputs for c in o.citations}.values())
        artifacts = [a for o in outputs for a in o.artifacts]
        agent_statuses = {
            o.domain: ("FAILED" if o.error else "PARTIAL" if o.partial else "COMPLETED")
            for o in outputs
        }
        is_partial = any(o.partial or o.error for o in outputs)

        # --- Checkpoint: FINDINGS_READY ---
        if session.needs_checkpoint(CheckpointType.FINDINGS_READY):
            cp = session.record_checkpoint(
                CheckpointType.FINDINGS_READY,
                {
                    "finding_count": len(findings),
                    "agent_statuses": agent_statuses,
                    "is_partial": is_partial,
                },
            )
            if on_checkpoint:
                await on_checkpoint(cp)
            else:
                await session.wait_for_approval(cp)
            logger.info("Checkpoint FINDINGS_READY approved")

        executive_summary = await self._write_summary(findings, mode, repo_url)

        package = ReviewPackage(
            run_id=run_id,
            repo_url=repo_url,
            mode=mode,
            duration_seconds=time.monotonic() - start,
            executive_summary=executive_summary,
            findings=sorted(
                findings,
                key=lambda f: ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"].index(f.severity.value),
            ),
            artifacts=artifacts,
            citations=citations,
            agent_statuses=agent_statuses,
            partial=is_partial,
            model_version=settings.agent_model,
        )

        # --- Checkpoint: PACKAGE_READY ---
        if session.needs_checkpoint(CheckpointType.PACKAGE_READY):
            cp = session.record_checkpoint(
                CheckpointType.PACKAGE_READY,
                {
                    "finding_count": len(findings),
                    "duration_seconds": package.duration_seconds,
                },
            )
            if on_checkpoint:
                await on_checkpoint(cp)
            else:
                await session.wait_for_approval(cp)
            logger.info("Checkpoint PACKAGE_READY approved")

        return package

    def _deduplicate(self, findings: list[Finding]) -> list[Finding]:
        seen: dict[str, Finding] = {}
        for f in findings:
            key = f"{f.severity.value}:{f.title.lower()[:60]}"
            if key not in seen:
                seen[key] = f
        return list(seen.values())

    async def _write_summary(self, findings: list[Finding], mode: str, repo_url: str) -> str:
        critical = sum(1 for f in findings if f.severity.value == "CRITICAL")
        high = sum(1 for f in findings if f.severity.value == "HIGH")
        top_titles = "; ".join(f.title for f in findings[:5])
        prompt = (
            f"You are the ARCHON supervisor. Write a concise executive summary (max 300 words) for a {mode} "
            f"architecture review of {repo_url}. There are {critical} CRITICAL and {high} HIGH findings. "
            f"Top findings: {top_titles}. "
            "Focus on business risk, not technical jargon. Be specific and actionable."
        )
        try:
            return await self._llm.complete(
                "You are an expert architect creating executive summaries.",
                prompt,
                thinking_budget="low",
            )
        except Exception:
            return (
                f"Architecture review complete. {len(findings)} findings "
                f"({critical} critical, {high} high)."
            )
