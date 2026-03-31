from __future__ import annotations
from typing import AsyncGenerator

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas.auth import CurrentUser


async def get_current_user(request: Request) -> CurrentUser:
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


async def require_user(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    return user


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    from db.connection import async_session_factory
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
