from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from api.dependencies import require_user
from api.schemas.auth import CurrentUser
from api.services.review_service import check_plan_limit, create_review
from archon.input.cost_parser import CostParser
from archon.input.iac_parser import IaCParser

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cost-optimiser", tags=["cost-optimiser"])


@router.post("/analyse", status_code=status.HTTP_202_ACCEPTED)
async def analyse_cost_optimiser(
    repo_url: str = Form(...),
    cost_csv: UploadFile | None = File(default=None),
    iac_file: UploadFile | None = File(default=None),
    user: CurrentUser = Depends(require_user),
) -> dict:
    if not repo_url.startswith("https://github.com/"):
        raise HTTPException(status_code=400, detail="Only github.com repos supported")

    allowed, reason = await check_plan_limit(user.user_id)
    if not allowed:
        raise HTTPException(status_code=402, detail=reason)

    parsed_summary: dict = {}
    if cost_csv is not None:
        try:
            content = await cost_csv.read()
            parsed = await CostParser().parse(content)
            parsed_summary["cost"] = parsed.metadata
        except Exception as exc:
            logger.warning("Cost CSV parse failed: %s", exc)

    if iac_file is not None:
        try:
            content = await iac_file.read()
            parsed = await IaCParser().parse(content)
            parsed_summary["iac"] = parsed.metadata
        except Exception as exc:
            logger.warning("IaC parse failed: %s", exc)

    review_id, job_id = await create_review(user.user_id, repo_url, "cost_optimiser")
    logger.info(
        "Cost optimiser queued review=%s job=%s repo=%s metadata=%s",
        review_id,
        job_id,
        repo_url,
        bool(parsed_summary),
    )
    return {
        "review_id": review_id,
        "job_id": job_id,
        "status": "QUEUED",
        "mode": "cost_optimiser",
    }
