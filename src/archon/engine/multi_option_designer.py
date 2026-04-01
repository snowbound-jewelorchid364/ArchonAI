from __future__ import annotations
import json
import logging
import re

from pydantic import BaseModel

from ..core.models.review_package import ReviewPackage
from ..core.models.artifact import Artifact, ArtifactType
from ..core.ports.llm_port import LLMPort
from .requirements_translator import TechnicalConstraints

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are an architecture advisor. Given findings and constraints, generate exactly 3 architecture options: Lean MVP, Growth-Ready, Enterprise-Scale.
Each must be realistic for the given budget and timeline. Return a JSON array only — no explanation, no markdown fences.

JSON shape (array of 3 objects):
[
  {
    "id": "lean",
    "name": "Lean MVP",
    "tagline": "one sentence",
    "monthly_cost_estimate": "$150-400/month",
    "team_size": "1-2 engineers",
    "time_to_mvp": "4-6 weeks",
    "tech_stack": ["React", "Node.js", "PostgreSQL", "Vercel"],
    "key_tradeoffs": ["Fast to build", "Limited scalability past 10k users"],
    "adrs": ["ADR-001: Use managed database", "ADR-002: Monolith-first"],
    "suitable_for": "Solo founders validating the idea with <1000 users"
  },
  { "id": "scalable", ... },
  { "id": "enterprise", ... }
]

Rules:
- If budget < $500/month: Lean must NOT include Kubernetes, EKS, GKE, or AKS
- If timeline < 8 weeks: Lean must be achievable in that timeline
- Enterprise option must cost at least 10x Lean option
- All three must share the same core feature set but differ in scale and ops complexity
- Be specific with technology names (not "a database" but "PostgreSQL" or "DynamoDB")
"""


class ArchitectureOption(BaseModel):
    id: str
    name: str
    tagline: str
    monthly_cost_estimate: str
    team_size: str
    time_to_mvp: str
    tech_stack: list[str]
    key_tradeoffs: list[str]
    adrs: list[str]
    suitable_for: str


_FALLBACK_OPTIONS: list[dict] = [
    {
        "id": "lean",
        "name": "Lean MVP",
        "tagline": "Ship fast, validate the idea, iterate based on real users.",
        "monthly_cost_estimate": "$50-200/month",
        "team_size": "1-2 engineers",
        "time_to_mvp": "4-6 weeks",
        "tech_stack": ["Next.js", "PostgreSQL", "Vercel", "Stripe"],
        "key_tradeoffs": ["Fast time-to-market", "Limited scalability past 10k users", "Some technical debt expected"],
        "adrs": ["ADR-001: Monolith-first architecture", "ADR-002: Managed database to reduce ops"],
        "suitable_for": "Solo founders or small teams validating product-market fit",
    },
    {
        "id": "scalable",
        "name": "Growth-Ready",
        "tagline": "Built to scale from day one without a full rewrite.",
        "monthly_cost_estimate": "$500-2000/month",
        "team_size": "3-5 engineers",
        "time_to_mvp": "8-12 weeks",
        "tech_stack": ["Next.js", "FastAPI", "PostgreSQL", "Redis", "AWS ECS", "CloudFront"],
        "key_tradeoffs": ["Higher initial cost", "Requires DevOps expertise", "Scales to 100k+ users"],
        "adrs": ["ADR-001: API-first separation", "ADR-002: Container-based deployment", "ADR-003: CDN for static assets"],
        "suitable_for": "Teams with seed funding targeting rapid user growth",
    },
    {
        "id": "enterprise",
        "name": "Enterprise-Scale",
        "tagline": "Production-grade infrastructure with multi-region resilience.",
        "monthly_cost_estimate": "$5000-20000/month",
        "team_size": "8-15 engineers",
        "time_to_mvp": "16-24 weeks",
        "tech_stack": ["Next.js", "Microservices", "Kubernetes (EKS)", "Aurora", "Elasticsearch", "Terraform"],
        "key_tradeoffs": ["High operational complexity", "Requires SRE team", "Full compliance and audit support"],
        "adrs": ["ADR-001: Microservices architecture", "ADR-002: Kubernetes orchestration", "ADR-003: Multi-region deployment"],
        "suitable_for": "Series A+ companies or enterprises requiring SLAs and compliance",
    },
]


async def generate_options(
    package: ReviewPackage,
    constraints: TechnicalConstraints,
    llm: LLMPort,
) -> list[ArchitectureOption]:
    """Call Claude to generate 3 architecture options from the review package."""

    findings_summary = "\n".join(
        f"- [{f.severity.value}] {f.title}: {f.recommendation}"
        for f in package.findings[:20]
    )

    constraints_summary = (
        f"User type: {constraints.user_type}\n"
        f"Estimated RPS at Y1: {constraints.estimated_rps}\n"
        f"Monthly budget: ${constraints.budget_monthly_usd}\n"
        f"Timeline: {constraints.timeline_weeks} weeks\n"
        f"Compliance: {constraints.compliance_requirements or ['none']}\n"
        f"Team size hint: {constraints.team_size_hint}"
    )

    user_msg = (
        f"Architecture findings:\n{findings_summary}\n\n"
        f"Technical constraints:\n{constraints_summary}\n\n"
        "Generate exactly 3 options (lean, scalable, enterprise) as a JSON array."
    )

    try:
        raw = await llm.complete(_SYSTEM_PROMPT, user_msg, max_tokens=2048)
        text = raw.strip()
        text = re.sub(r"^```[a-z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        data = json.loads(text)
        options = [ArchitectureOption(**item) for item in data]
        if len(options) != 3:
            raise ValueError(f"Expected 3 options, got {len(options)}")
    except Exception as exc:
        logger.warning("generate_options LLM call failed: %s — using fallback options", exc)
        options = [ArchitectureOption(**o) for o in _FALLBACK_OPTIONS]

    # Budget validation: Lean must not include Kubernetes if budget < $500
    if constraints.budget_monthly_usd < 500:
        lean = next((o for o in options if o.id == "lean"), None)
        if lean:
            k8s_terms = {"kubernetes", "eks", "gke", "aks", "k8s"}
            lean.tech_stack = [t for t in lean.tech_stack if t.lower() not in k8s_terms]

    # Store options as an artifact on the package
    import uuid as _uuid
    options_artifact = Artifact(
        id=str(_uuid.uuid4()),
        artifact_type=ArtifactType.DIAGRAM,
        title="Architecture Options",
        content=json.dumps([o.model_dump() for o in options], indent=2),
        filename="architecture_options.json",
    )
    package.artifacts.append(options_artifact)

    return options
