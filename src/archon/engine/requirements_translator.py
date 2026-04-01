from __future__ import annotations
import json
import logging
import re

from pydantic import BaseModel

from ..core.ports.llm_port import LLMPort
from ..config.settings import settings
from .intake import ProductBrief

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are a requirements analyst. Convert the product brief to technical constraints.
Return JSON only — no explanation, no markdown fences.

JSON shape:
{
  "user_type": "B2C" | "B2B" | "internal",
  "estimated_rps": <integer, requests per second at Y1 scale>,
  "budget_monthly_usd": <integer>,
  "timeline_weeks": <integer>,
  "compliance_requirements": ["HIPAA"] or [],
  "team_size_hint": "solo" | "small" | "medium" | "large",
  "suggested_options": ["lean", "scalable", "enterprise"]
}

Rules for estimation:
- 1 000 users -> 5 rps, 10 000 users -> 50 rps, 100 000 users -> 500 rps
- Parse budget strings: "$500/month" -> 500, "~$1k" -> 1000, "500 dollars monthly" -> 500
- Parse timeline: "3 months" -> 13 weeks, "6 weeks" -> 6, "ASAP" -> 4
- Detect compliance: mentions of HIPAA, GDPR, PCI, SOX, FINRA -> include in list
- team_size_hint: solo (1 person), small (2-3), medium (4-10), large (10+); default to "small"
"""


_FALLBACK = {
    "user_type": "B2C",
    "estimated_rps": 10,
    "budget_monthly_usd": 500,
    "timeline_weeks": 12,
    "compliance_requirements": [],
    "team_size_hint": "small",
    "suggested_options": ["lean", "scalable", "enterprise"],
}


class TechnicalConstraints(BaseModel):
    user_type: str
    estimated_rps: int
    budget_monthly_usd: int
    timeline_weeks: int
    compliance_requirements: list[str]
    team_size_hint: str
    suggested_options: list[str]


def _default_constraints() -> TechnicalConstraints:
    return TechnicalConstraints(**_FALLBACK)


def _extract_compliance(text: str) -> list[str]:
    found = []
    for tag in ("HIPAA", "GDPR", "PCI", "SOX", "FINRA", "ISO 27001", "FedRAMP"):
        if tag.lower() in text.lower():
            found.append(tag)
    return found


async def translate(brief: ProductBrief, llm: LLMPort) -> TechnicalConstraints:
    """Call Claude (fast model) to convert a ProductBrief to TechnicalConstraints."""
    user_msg = f"""Product idea: {brief.idea}
Users: {brief.users}
Core value: {brief.core_value}
Year-1 scale: {brief.scale_y1}
Year-2 scale: {brief.scale_y2}
Monthly budget: {brief.budget_monthly}
Timeline: {brief.timeline}
Compliance: {brief.compliance}"""

    # Override the model to fast_model for this quick translation step
    original_model = None
    try:
        original_model = settings.agent_model
        object.__setattr__(settings, "agent_model", settings.fast_model)
        raw = await llm.complete(_SYSTEM_PROMPT, user_msg, max_tokens=512)
    except Exception as exc:
        logger.warning("LLM call failed in translate: %s — using fallback", exc)
        return _default_constraints()
    finally:
        if original_model is not None:
            try:
                object.__setattr__(settings, "agent_model", original_model)
            except Exception:
                pass

    try:
        # Strip markdown fences if present
        text = raw.strip()
        text = re.sub(r"^```[a-z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        data = json.loads(text)
        constraints = TechnicalConstraints(**{**_FALLBACK, **data})
        # Ensure compliance also catches explicit mentions in brief
        extra = _extract_compliance(brief.compliance + " " + brief.users)
        for tag in extra:
            if tag not in constraints.compliance_requirements:
                constraints.compliance_requirements.append(tag)
        return constraints
    except Exception as exc:
        logger.warning("Failed to parse TechnicalConstraints JSON: %s — using fallback", exc)
        # Still try to extract compliance from the brief text
        fallback = _default_constraints()
        fallback.compliance_requirements = _extract_compliance(brief.compliance + " " + brief.users)
        return fallback
