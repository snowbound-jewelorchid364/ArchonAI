from __future__ import annotations
import re
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import DecisionHistoryRow
from archon.core.models.review_package import ReviewPackage
from archon.core.models.artifact import ArtifactType

logger = logging.getLogger(__name__)


def _extract_section(markdown: str, heading: str) -> str:
    pattern = rf"## {heading}\s*\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, markdown, re.DOTALL)
    return match.group(1).strip() if match else ""


async def save_decisions(
    db: AsyncSession,
    user_id: str,
    review_id: str,
    package: ReviewPackage,
) -> None:
    for artifact in package.artifacts:
        if artifact.artifact_type != ArtifactType.ADR:
            continue
        decision = _extract_section(artifact.content, "Decision")
        rationale = _extract_section(artifact.content, "Rationale")
        row = DecisionHistoryRow(
            user_id=user_id,
            review_id=review_id,
            repo_url=package.repo_url,
            adr_title=artifact.title,
            decision=decision or artifact.content[:500],
            rationale=rationale or "",
            status="active",
        )
        db.add(row)
    await db.flush()


async def get_decisions(
    db: AsyncSession,
    user_id: str,
    repo_url: str | None = None,
    limit: int = 20,
) -> list[DecisionHistoryRow]:
    stmt = (
        select(DecisionHistoryRow)
        .where(DecisionHistoryRow.user_id == user_id)
        .order_by(DecisionHistoryRow.created_at.desc())
        .limit(limit)
    )
    if repo_url:
        stmt = stmt.where(DecisionHistoryRow.repo_url == repo_url)
    result = await db.execute(stmt)
    return list(result.scalars().all())
