from __future__ import annotations

import os
from typing import Annotated
from urllib.parse import unquote

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.dependencies import get_current_user
from api.schemas.auth import CurrentUser
from archon.infrastructure.cache.redis_cache import RedisCache
from archon.mcp.connector_registry import CONNECTORS, fetch_connector_context


router = APIRouter(prefix="/connectors", tags=["connectors"])


class ConnectorFetchRequest(BaseModel):
    repo_url: str = Field(..., min_length=1)
    aws_region: str = "us-east-1"


@router.get("")
async def list_connectors(
    _: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict:
    status = {
        "github": {
            "available": True,
            "configured": bool(os.getenv("GITHUB_TOKEN", "")),
        },
        "aws": {
            "available": True,
            "configured": bool(os.getenv("AWS_ACCESS_KEY_ID", "") and os.getenv("AWS_SECRET_ACCESS_KEY", "")),
        },
        "slack": {
            "available": True,
            "configured": bool(os.getenv("SLACK_BOT_TOKEN", "")),
        },
    }
    return {"connectors": list(CONNECTORS.keys()), "status": status}


@router.post("/{name}/fetch")
async def fetch_connector(
    name: str,
    body: ConnectorFetchRequest,
    _: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict:
    if name not in CONNECTORS:
        raise HTTPException(status_code=404, detail=f"Unknown connector: {name}")

    kwargs = {"repo_url": body.repo_url}
    if name == "aws":
        kwargs["aws_region"] = body.aws_region

    ctx = await fetch_connector_context(name, **kwargs)
    if ctx is None:
        raise HTTPException(status_code=502, detail=f"Connector fetch failed: {name}")

    key = f"connector:{name}:{body.repo_url}"
    cache = RedisCache()
    try:
        await cache.connect()
        await cache.set(key, ctx.model_dump(), ttl_seconds=3600)
    except Exception:
        # Cache failures should not block connector fetch responses.
        pass
    finally:
        try:
            await cache.close()
        except Exception:
            pass

    return ctx.model_dump()


@router.get("/{name}/context/{repo:path}")
async def get_cached_connector_context(
    name: str,
    repo: str,
    _: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict:
    if name not in CONNECTORS:
        raise HTTPException(status_code=404, detail=f"Unknown connector: {name}")

    repo_url = unquote(repo)
    key = f"connector:{name}:{repo_url}"

    cache = RedisCache()
    try:
        await cache.connect()
        data = await cache.get(key)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Cache unavailable: {exc}")
    finally:
        try:
            await cache.close()
        except Exception:
            pass

    if not data:
        raise HTTPException(status_code=404, detail="No cached context found")
    return data
