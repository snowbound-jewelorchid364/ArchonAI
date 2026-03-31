"""Shared JSON response parser for agent outputs."""
from __future__ import annotations
import json
import logging
import re
from ..core.models import Finding, Artifact, Citation, ArtifactType, Severity

logger = logging.getLogger(__name__)


def parse_agent_json(raw: str, domain: str) -> dict:
    """Parse LLM JSON response with multiple fallback strategies."""
    cleaned = raw.strip()

    # Strategy 1: Strip markdown fences
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)

    # Strategy 2: Find outermost braces
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        logger.warning("[%s] No JSON object found in response", domain)
        return {"findings": [], "artifacts": [], "confidence": 0.3}

    json_str = cleaned[start : end + 1]

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as exc:
        logger.warning("[%s] JSON parse failed: %s", domain, exc)
        # Strategy 3: Try fixing common issues
        fixed = json_str.replace(",]", "]").replace(",}", "}")
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            logger.error("[%s] JSON parse failed after fix attempt", domain)
            return {"findings": [], "artifacts": [], "confidence": 0.2}


def build_findings(data: dict, domain: str) -> list[Finding]:
    """Build Finding objects from parsed JSON, handling malformed entries."""
    findings = []
    for i, f in enumerate(data.get("findings", [])):
        try:
            if "domain" not in f:
                f["domain"] = domain
            if "id" not in f:
                prefix = domain.split("-")[0].upper()[:3]
                f["id"] = f"{prefix}-{i + 1:03d}"
            if "severity" in f and isinstance(f["severity"], str):
                f["severity"] = f["severity"].upper()
            findings.append(Finding(**f))
        except Exception as exc:
            logger.warning("[%s] Skipping malformed finding %d: %s", domain, i, exc)
    return findings


def build_artifacts(data: dict) -> list[Artifact]:
    """Build Artifact objects from parsed JSON."""
    artifacts = []
    for a in data.get("artifacts", []):
        try:
            artifacts.append(Artifact(**a))
        except Exception as exc:
            logger.warning("Skipping malformed artifact: %s", exc)
    return artifacts


def build_citations(search_results: list) -> list[Citation]:
    """Convert search results to Citation objects."""
    citations = []
    for r in search_results:
        try:
            citations.append(Citation(
                url=str(r.url),
                title=r.title,
                excerpt=r.excerpt[:300] if r.excerpt else "",
                published_date=getattr(r, "published_date", None),
                credibility_score=getattr(r, "score", 0.5),
            ))
        except Exception:
            continue
    return citations
