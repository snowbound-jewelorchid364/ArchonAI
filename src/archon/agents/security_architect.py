from __future__ import annotations
import logging
from ..core.models import AgentOutput
from .base import BaseArchitectAgent
from .parser import parse_agent_json, build_findings, build_artifacts, build_citations

logger = logging.getLogger(__name__)


class SecurityArchitectAgent(BaseArchitectAgent):
    domain = "security-architect"
    _prompt_path = "security_architect.md"

    async def _analyse(self, repo_context: str, mode: str, mode_focus: str = "") -> AgentOutput:
        search_results = await self._search("zero trust security architecture CVE OWASP IAM encryption compliance 2025", max_results=5)
        citations = build_citations(search_results)
        citation_ctx = chr(10).join(f"- {c.title}: {c.excerpt[:200]}" for c in citations[:5])

        focus_line = f"Mode focus: {mode_focus}" if mode_focus else ""

        user_msg = f"""Mode: {mode}
{focus_line}

Codebase context:
{repo_context}

Web research:
{citation_ctx}

Analyse security: zero-trust gaps, IAM issues, encryption at rest/transit, CVEs, OWASP Top 10, compliance gaps.

Return JSON only: {"findings": [{"id": "SEC-001", "title": "string", "description": "string referencing actual security config", "severity": "CRITICAL|HIGH|MEDIUM|LOW|INFO", "domain": "security-architect", "file_path": "string or null", "line_number": null, "recommendation": "concrete actionable string", "citations": [], "confidence": 0.0, "from_codebase": true}], "artifacts": [], "confidence": 0.0}"""

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
