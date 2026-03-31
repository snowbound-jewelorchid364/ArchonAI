from __future__ import annotations
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from .models import Base

logger = logging.getLogger(__name__)

_engine = None
_session_factory = None


def init_db(database_url: str) -> None:
    global _engine, _session_factory
    _engine = create_async_engine(
        database_url,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )
    _session_factory = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)


async def create_tables() -> None:
    if _engine is None:
        raise RuntimeError("Call init_db() first")
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables() -> None:
    if _engine is None:
        raise RuntimeError("Call init_db() first")
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if _session_factory is None:
        raise RuntimeError("Call init_db() first")
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def shutdown_db() -> None:
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None
