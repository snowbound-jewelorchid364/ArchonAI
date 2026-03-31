from __future__ import annotations
import io
import json
import zipfile
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from ..schemas.auth import CurrentUser
from ..dependencies import require_user
from ..services.review_service import get_review

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{review_id}/download")
async def download_package(
    review_id: str,
    user: CurrentUser = Depends(require_user),
) -> StreamingResponse:
    review = await get_review(review_id, user.user_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.status not in {"COMPLETED", "PARTIAL"}:
        raise HTTPException(status_code=400, detail=f"Review not ready (status: {review.status})")

    if not review.package_json:
        raise HTTPException(status_code=404, detail="Package data not available")

    package = review.package_json
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # README / executive summary
        summary = review.executive_summary or "Review package"
        zf.writestr("README.md", f"# ARCHON Architecture Review\n\n{summary}\n")

        # Findings by domain
        findings = package.get("findings", [])
        domains: dict[str, list] = {}
        for f in findings:
            domain = f.get("domain", "general")
            domains.setdefault(domain, []).append(f)

        for domain, domain_findings in domains.items():
            content = f"# {domain.replace('-', ' ').title()} Findings\n\n"
            for f in domain_findings:
                severity = f.get("severity", "INFO")
                content += f"## [{severity}] {f.get('title', 'Untitled')}\n\n"
                content += f"{f.get('description', '')}\n\n"
                if f.get("file_path"):
                    content += f"**File:** `{f['file_path']}`\n\n"
                content += f"**Recommendation:** {f.get('recommendation', 'N/A')}\n\n---\n\n"
            zf.writestr(f"findings/{domain}.md", content)

        # Risk register
        risk_content = "# Risk Register\n\n| Severity | Title | Domain | Confidence |\n|---|---|---|---|\n"
        for f in sorted(findings, key=lambda x: ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"].index(x.get("severity", "INFO"))):
            risk_content += f"| {f.get('severity')} | {f.get('title')} | {f.get('domain')} | {f.get('confidence', 0):.0%} |\n"
        zf.writestr("risk-register.md", risk_content)

        # Citations
        citations = package.get("citations", [])
        if citations:
            cit_content = "# Citations\n\n"
            for c in citations:
                cit_content += f"- [{c.get('title', 'Source')}]({c.get('url', '')})\n"
                if c.get("excerpt"):
                    cit_content += f"  > {c['excerpt'][:200]}\n\n"
            zf.writestr("citations.md", cit_content)

        # Agent statuses
        if review.agent_statuses:
            status_content = "# Agent Status\n\n| Agent | Status |\n|---|---|\n"
            for agent, s in review.agent_statuses.items():
                status_content += f"| {agent} | {s} |\n"
            zf.writestr("agent-status.md", status_content)

    buffer.seek(0)
    filename = f"archon-review-{review_id[:8]}.zip"

    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
