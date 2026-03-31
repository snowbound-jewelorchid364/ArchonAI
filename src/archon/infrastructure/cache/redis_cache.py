from __future__ import annotations
import json
import redis.asyncio as redis
from ...config.settings import settings


class RedisCache:
    def __init__(self) -> None:
        self._client: redis.Redis | None = None

    async def connect(self) -> None:
        self._client = redis.from_url(settings.redis_url, decode_responses=True)

    async def set(self, key: str, value: object, ttl_seconds: int = 3600) -> None:
        assert self._client is not None
        await self._client.setex(key, ttl_seconds, json.dumps(value))

    async def get(self, key: str) -> object | None:
        assert self._client is not None
        raw = await self._client.get(key)
        return json.loads(raw) if raw else None

    async def delete(self, key: str) -> None:
        assert self._client is not None
        await self._client.delete(key)

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
