from __future__ import annotations
import logging
from ..core.models import AgentOutput
from .base import BaseArchitectAgent
from .parser import parse_agent_json, build_findings, build_artifacts, build_citations

logger = logging.getLogger(__name__)


class CloudArchitectAgent(BaseArchitectAgent):
    domain = "cloud-architect"
    _prompt_path = "cloud_architect.md"

    async def _analyse(self, repo_context: str, mode: str) -> AgentOutput:
        search_results = await self._search("cloud infrastructure AWS GCP Azure FinOps cost optimization 2025", max_results=5)
        citations = build_citations(search_results)
        citation_ctx = chr(10).join(f"- {c.title}: {c.excerpt[:200]}" for c in citations[:5])

        user_msg = f"""Mode: {mode}

Codebase context:
{repo_context}

Web research:
{citation_ctx}

Analyse cloud architecture: provider usage, IaC quality, cost optimization, scalability, DR, networking.

Return JSON only: {"findings": [{"id": "CA-001", "title": "string", "description": "string referencing actual files", "severity": "CRITICAL|HIGH|MEDIUM|LOW|INFO", "domain": "cloud-architect", "file_path": "string or null", "line_number": null, "recommendation": "concrete actionable string", "citations": [], "confidence": 0.0, "from_codebase": true}], "artifacts": [], "confidence": 0.0}"""

        raw = await self._llm.complete(self._system_prompt, user_msg)
        data = parse_agent_json(raw, self.domain)

        return AgentOutput(
            domain=self.domain,
            findings=build_findings(data, self.domain),
            citations=citations,
            artifacts=build_artifacts(data),
            confidence=float(data.get("confidence", 0.7)),
            duration_seconds=0.0,
        )
