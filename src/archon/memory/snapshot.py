from __future__ import annotations
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ArchitectureSnapshotRow
from archon.core.models.review_package import ReviewPackage
from archon.memory.decisions import get_decisions

logger = logging.getLogger(__name__)


async def save_snapshot(
    db: AsyncSession,
    user_id: str,
    review_id: str,
    package: ReviewPackage,
) -> None:
    domains: dict[str, int] = {}
    for f in package.findings:
        domain = f.domain.lower()
        domains[domain] = domains.get(domain, 0) + 1

    row = ArchitectureSnapshotRow(
        user_id=user_id,
        review_id=review_id,
        repo_url=package.repo_url,
        mode=package.mode,
        summary=package.executive_summary[:2000],
        finding_count=len(package.findings),
        critical_count=len(package.critical_findings),
        high_count=len(package.high_findings),
        domains_json=domains,
    )
    db.add(row)
    await db.flush()


async def get_snapshots(
    db: AsyncSession,
    user_id: str,
    repo_url: str | None = None,
    limit: int = 20,
) -> list[ArchitectureSnapshotRow]:
    stmt = (
        select(ArchitectureSnapshotRow)
        .where(ArchitectureSnapshotRow.user_id == user_id)
        .order_by(ArchitectureSnapshotRow.created_at.desc())
        .limit(limit)
    )
    if repo_url:
        stmt = stmt.where(ArchitectureSnapshotRow.repo_url == repo_url)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def build_memory_context(
    db: AsyncSession,
    user_id: str,
    repo_url: str,
) -> str:
    snapshots = await get_snapshots(db, user_id, repo_url, limit=5)
    decisions = await get_decisions(db, user_id, repo_url, limit=10)

    if not snapshots and not decisions:
        return ""

    lines = ["## Architecture History for this Repository\n"]

    if snapshots:
        lines.append("### Past Reviews")
        for s in snapshots:
            lines.append(
                f"- {s.created_at.strftime('%Y-%m-%d')} | {s.mode} | "
                f"{s.finding_count} findings ({s.critical_count} critical, {s.high_count} high)\n"
                f"  Summary: {s.summary[:300]}"
            )

    if decisions:
        lines.append("\n### Past Decisions (ADRs)")
        for d in decisions:
            status_note = " [VIOLATED]" if d.status == "violated" else ""
            lines.append(
                f"- [{d.status.upper()}{status_note}] {d.adr_title}: {d.decision[:200]}"
            )

    return "\n".join(lines)
