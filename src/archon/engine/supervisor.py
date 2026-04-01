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
from .modes.configs import get_mode, ModeConfig
from .hitl.checkpoints import HITLMode, CheckpointType
from .hitl.session import HITLSession

logger = logging.getLogger(__name__)

AGENT_REGISTRY: dict[str, type] = {
    "software": SoftwareArchitectAgent,
    "cloud": CloudArchitectAgent,
    "security": SecurityArchitectAgent,
    "data": DataArchitectAgent,
    "integration": IntegrationArchitectAgent,
    "ai": AiArchitectAgent,
}

# Per-mode HITL overrides: Incident = no checkpoints (speed), Due Diligence = all
MODE_HITL_OVERRIDES: dict[str, HITLMode] = {
    "incident_responder": HITLMode.AUTOPILOT,
}

# Modes that FORCE full supervised regardless of user choice
MODE_HITL_MINIMUM: dict[str, HITLMode] = {
    "due_diligence": HITLMode.SUPERVISED,
    "compliance_auditor": HITLMode.BALANCED,
}


class Supervisor:
    def __init__(self, llm: LLMPort, searchers: list[SearchPort], retriever: RAGRetriever) -> None:
        self._llm = llm
        self._searchers = searchers
        self._retriever = retriever

    def _build_agents(self, mode_config: ModeConfig) -> list:
        agents = []
        for agent_key in mode_config.active_agents:
            cls = AGENT_REGISTRY.get(agent_key)
            if cls:
                agents.append(cls(self._llm, self._searchers, self._retriever))
            else:
                logger.warning("Unknown agent key: %s", agent_key)
        return agents

    def _resolve_hitl(self, mode: str, requested: HITLMode) -> HITLMode:
        if mode in MODE_HITL_OVERRIDES:
            return MODE_HITL_OVERRIDES[mode]
        if mode in MODE_HITL_MINIMUM:
            minimum = MODE_HITL_MINIMUM[mode]
            rank = {HITLMode.AUTOPILOT: 0, HITLMode.BALANCED: 1, HITLMode.SUPERVISED: 2}
            return minimum if rank[minimum] > rank[requested] else requested
        return requested

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
        mode_config = get_mode(mode)
        thinking_budget = settings.thinking_budget_for_mode(mode)
        effective_hitl = self._resolve_hitl(mode, hitl_mode)
        session = HITLSession(job_id=run_id, hitl_mode=effective_hitl)

        # Build only the agents this mode needs
        agents = self._build_agents(mode_config)
        logger.info(
            "Supervisor starting | run=%s | mode=%s | agents=%s | thinking=%s | hitl=%s",
            run_id, mode, [a.domain for a in agents], thinking_budget, effective_hitl.value,
        )

        # --- Checkpoint: AGENTS_STARTED ---
        if session.needs_checkpoint(CheckpointType.AGENTS_STARTED):
            cp = session.record_checkpoint(
                CheckpointType.AGENTS_STARTED,
                {"agents": [a.domain for a in agents], "mode": mode, "focus": mode_config.supervisor_focus},
            )
            if on_checkpoint:
                await on_checkpoint(cp)
            else:
                await session.wait_for_approval(cp)

        # Fan out only active agents in parallel, passing mode focus as context
        results = await asyncio.gather(
            *[agent.run(mode, mode_focus=mode_config.supervisor_focus) for agent in agents],
            return_exceptions=True,
        )

        outputs: list[AgentOutput] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                agent_name = agents[i].domain
                logger.error("Agent %s raised: %s", agent_name, result)
                outputs.append(AgentOutput(
                    domain=agent_name, confidence=0.0, duration_seconds=0.0,
                    error=str(result), partial=True,
                ))
            else:
                outputs.append(result)

        findings = self._deduplicate([f for o in outputs for f in o.findings])
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
                {"finding_count": len(findings), "agent_statuses": agent_statuses, "is_partial": is_partial},
            )
            if on_checkpoint:
                await on_checkpoint(cp)
            else:
                await session.wait_for_approval(cp)

        executive_summary = await self._write_summary(findings, mode_config, repo_url)

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
                {"finding_count": len(findings), "duration_seconds": package.duration_seconds},
            )
            if on_checkpoint:
                await on_checkpoint(cp)
            else:
                await session.wait_for_approval(cp)

        return package

    def _deduplicate(self, findings: list[Finding]) -> list[Finding]:
        seen: dict[str, Finding] = {}
        for f in findings:
            key = f"{f.severity.value}:{f.title.lower()[:60]}"
            if key not in seen:
                seen[key] = f
        return list(seen.values())

    async def _write_summary(self, findings: list[Finding], mode_config: ModeConfig, repo_url: str) -> str:
        critical = sum(1 for f in findings if f.severity.value == "CRITICAL")
        high = sum(1 for f in findings if f.severity.value == "HIGH")
        top_titles = "; ".join(f.title for f in findings[:5])
        prompt = (
            f"You are the ARCHON supervisor. Write a concise executive summary (max 300 words) "
            f"for a {mode_config.name} architecture review of {repo_url}.\n\n"
            f"Mode focus: {mode_config.supervisor_focus}\n"
            f"Active agents: {', '.join(mode_config.active_agents)}\n"
            f"Required output sections: {', '.join(mode_config.output_sections)}\n\n"
            f"There are {critical} CRITICAL and {high} HIGH findings.\n"
            f"Top findings: {top_titles}.\n\n"
            "Write for the audience implied by the mode focus. Be specific and actionable."
        )
        try:
            return await self._llm.complete(
                "You are an expert architect creating executive summaries.",
                prompt, thinking_budget="low",
            )
        except Exception:
            return f"Review complete. {len(findings)} findings ({critical} critical, {high} high)."
