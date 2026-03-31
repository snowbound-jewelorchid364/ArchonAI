"""Handle review completion callbacks and post results to GitHub PRs."""
import logging
from typing import Any

from fastapi import APIRouter, Request, HTTPException

from .app import post_review_comment

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/callbacks/review-complete")
async def review_complete(request: Request):
    """Called by ARCHON API when a PR review is complete."""
    data = await request.json()

    installation_id = data.get("metadata", {}).get("installation_id")
    repo_full_name = data.get("repo_full_name", "")
    pr_number = data.get("metadata", {}).get("pr_number")
    findings = data.get("findings", [])

    if not all([installation_id, repo_full_name, pr_number]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    try:
        await post_review_comment(
            installation_id=installation_id,
            repo_full_name=repo_full_name,
            pr_number=pr_number,
            findings=findings,
        )
        return {"status": "comment_posted", "pr_number": pr_number}
    except Exception as e:
        logger.error(f"Failed to post comment: {e}")
        raise HTTPException(status_code=500, detail=str(e))
