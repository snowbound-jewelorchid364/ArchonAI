"""Build system prompt + context for architecture chat."""
from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from archon.core.models.review_package import ReviewPackage

from .history import ChatMessage

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are ARCHON's architecture advisor — a senior architect with deep expertise \
across software, cloud, security, data, integration, and AI/ML systems.

You are answering questions about a specific architecture review that has already been completed. \
Your answers must be:
- Grounded in the review findings provided in the context below
- Specific — reference actual files, service names, or patterns from the review when relevant
- Actionable — include concrete next steps the team can take
- Domain-aware — mention which specialist domain flagged each finding (software, cloud, security, etc.)

If the review context does not contain enough information to answer the question, say so clearly \
and explain what additional context would help rather than guessing.

Do NOT invent findings, file paths, or recommendations that are not present in the review context."""


_SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}


async def build_system_prompt(
    db: AsyncSession,
    review_id: str,
) -> str:
    """Return the system prompt with review findings embedded."""
    from db.models import ReviewRow

    result = await db.execute(
        select(ReviewRow).where(ReviewRow.id == review_id)
    )
    row = result.scalar_one_or_none()

    if not row:
        return _SYSTEM_PROMPT + "\n\n(No review found for this session.)"

    header = (
        f"\n\n---\n## Review Context\n"
        f"**Repository:** {row.repo_url}\n"
        f"**Mode:** {row.mode}\n"
        f"**Status:** {row.status}\n"
    )

    if not row.package_json:
        return _SYSTEM_PROMPT + header + "\n(Review is still running — findings not yet available.)"

    try:
        package = ReviewPackage.model_validate(row.package_json)
    except Exception as exc:
        logger.warning("Could not parse package_json for review %s: %s", review_id, exc)
        return _SYSTEM_PROMPT + header + "\n(Could not load review findings.)"

    sections = [_SYSTEM_PROMPT, header]

    if package.executive_summary:
        sections.append(f"\n### Executive Summary\n{package.executive_summary}")

    sorted_findings = sorted(
        package.findings,
        key=lambda f: _SEVERITY_ORDER.get(f.severity.value, 5),
    )

    if sorted_findings:
        lines = ["\n### Findings"]
        for f in sorted_findings:
            loc = f" `{f.file_path}:{f.line_number}`" if f.file_path else ""
            lines.append(
                f"\n**[{f.severity.value}] {f.title}**{loc} _(domain: {f.domain})_\n"
                f"{f.description}\n"
                f"_Recommendation:_ {f.recommendation}"
            )
        sections.append("\n".join(lines))

    return "\n".join(sections)


def format_history_for_claude(history: list[ChatMessage]) -> list[dict]:
    """Convert ChatMessage list to Anthropic messages format."""
    return [{"role": msg.role, "content": msg.content} for msg in history]
