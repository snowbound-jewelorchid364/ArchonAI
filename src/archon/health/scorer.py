from __future__ import annotations
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import HealthScoreRow
from archon.core.models.review_package import ReviewPackage
from archon.core.models.finding import Severity

logger = logging.getLogger(__name__)

SEVERITY_PENALTY: dict[Severity, float] = {
    Severity.CRITICAL: 15.0,
    Severity.HIGH: 7.0,
    Severity.MEDIUM: 3.0,
    Severity.LOW: 1.0,
    Severity.INFO: 0.0,
}

DOMAINS = ["software", "cloud", "security", "data", "integration", "ai"]

_WEIGHTS: dict[str, float] = {
    "software": 1.0,
    "cloud": 1.5,
    "security": 1.5,
    "data": 1.0,
    "integration": 1.0,
    "ai": 1.0,
}
_TOTAL_WEIGHT = sum(_WEIGHTS.values())


def compute_health_score(package: ReviewPackage) -> dict[str, float]:
    scores: dict[str, float] = {d: 100.0 for d in DOMAINS}

    for finding in package.findings:
        domain = finding.domain.lower()
        # Normalise agent-domain names like "software-architect" -> "software"
        for d in DOMAINS:
            if domain.startswith(d):
                domain = d
                break
        if domain in scores:
            scores[domain] = max(0.0, scores[domain] - SEVERITY_PENALTY.get(finding.severity, 0.0))

    overall = sum(scores[d] * _WEIGHTS[d] for d in DOMAINS) / _TOTAL_WEIGHT
    scores["overall"] = round(overall, 1)
    for d in DOMAINS:
        scores[d] = round(scores[d], 1)
    return scores


async def save_health_score(
    db: AsyncSession,
    user_id: str,
    review_id: str,
    package: ReviewPackage,
) -> HealthScoreRow:
    scores = compute_health_score(package)
    row = HealthScoreRow(
        user_id=user_id,
        review_id=review_id,
        repo_url=package.repo_url,
        overall=scores["overall"],
        software=scores["software"],
        cloud=scores["cloud"],
        security=scores["security"],
        data=scores["data"],
        integration=scores["integration"],
        ai=scores["ai"],
    )
    db.add(row)
    await db.flush()
    return row


async def get_score_history(
    db: AsyncSession,
    user_id: str,
    repo_url: str,
    limit: int = 30,
) -> list[HealthScoreRow]:
    result = await db.execute(
        select(HealthScoreRow)
        .where(HealthScoreRow.user_id == user_id, HealthScoreRow.repo_url == repo_url)
        .order_by(HealthScoreRow.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_latest_score(
    db: AsyncSession,
    user_id: str,
    repo_url: str,
) -> HealthScoreRow | None:
    result = await db.execute(
        select(HealthScoreRow)
        .where(HealthScoreRow.user_id == user_id, HealthScoreRow.repo_url == repo_url)
        .order_by(HealthScoreRow.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()
