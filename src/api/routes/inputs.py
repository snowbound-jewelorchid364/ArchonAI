from __future__ import annotations
import importlib
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.dependencies import get_current_user, get_db
from api.schemas.auth import CurrentUser
from db.models import ReviewRow

router = APIRouter(prefix="/reviews/{review_id}/inputs", tags=["inputs"])

PARSER_MAP = {
    "pdf": "archon.input.pdf_parser.PdfParser",
    "image": "archon.input.image_parser.ImageParser",
    "website": "archon.input.website_parser.WebsiteParser",
    "iac": "archon.input.iac_parser.IaCParser",
    "sql": "archon.input.sql_parser.SqlParser",
    "openapi": "archon.input.openapi_parser.OpenApiParser",
    "zip": "archon.input.zip_parser.ZipParser",
}

_TEXT_TYPES = {"iac", "sql", "openapi"}


@router.post("")
async def upload_input(
    review_id: str,
    type: str = Form(...),
    file: UploadFile = File(None),
    url: str = Form(None),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ReviewRow).where(ReviewRow.id == review_id, ReviewRow.user_id == user.user_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Review not found")

    if type not in PARSER_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported type: {type}. Must be one of: {list(PARSER_MAP.keys())}",
        )

    module_path, class_name = PARSER_MAP[type].rsplit(".", 1)
    module = importlib.import_module(module_path)
    parser_cls = getattr(module, class_name)
    parser = parser_cls()

    try:
        if type == "website":
            if not url:
                raise HTTPException(status_code=400, detail="url field required for website type")
            parsed = await parser.parse(url)
        else:
            if not file:
                raise HTTPException(status_code=400, detail="file field required for this type")
            content = await file.read()
            source = content.decode("utf-8", errors="replace") if type in _TEXT_TYPES else content
            parsed = await parser.parse(source)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    try:
        from archon.infrastructure.cache.redis_cache import RedisCache
        from archon.config.settings import settings
        cache = RedisCache(settings.redis_url)
        key = f"input:{review_id}:{type}"
        await cache.set(key, parsed.model_dump_json(), ttl=86400)
    except Exception:
        pass  # Redis unavailable — non-fatal

    return {
        "source_type": parsed.source_type,
        "title": parsed.title,
        "content_preview": parsed.content[:500],
        "metadata": parsed.metadata,
    }
