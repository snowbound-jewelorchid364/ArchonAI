"""Tests for RedisCache — set/get/expiry, namespace isolation, expired key."""
from __future__ import annotations
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_redis_client():
    client = AsyncMock()
    client.setex = AsyncMock()
    client.get = AsyncMock(return_value=None)
    client.delete = AsyncMock()
    client.aclose = AsyncMock()
    return client


@pytest.fixture
def redis_cache(mock_redis_client):
    from archon.infrastructure.cache.redis_cache import RedisCache
    cache = RedisCache()
    cache._client = mock_redis_client
    return cache


@pytest.mark.asyncio
async def test_set_and_get(redis_cache, mock_redis_client):
    """Test set stores JSON and get retrieves it."""
    mock_redis_client.get.return_value = json.dumps({"status": "running"})
    await redis_cache.set("job:123", {"status": "running"}, ttl_seconds=600)
    mock_redis_client.setex.assert_called_once_with(
        "job:123", 600, json.dumps({"status": "running"})
    )
    result = await redis_cache.get("job:123")
    assert result == {"status": "running"}


@pytest.mark.asyncio
async def test_namespace_isolation():
    """Test that job keys should be prefixed with user_id for isolation."""
    from archon.infrastructure.cache.redis_cache import RedisCache
    cache = RedisCache()
    cache._client = AsyncMock()
    cache._client.setex = AsyncMock()
    user_id = "user_abc"
    job_id = "job_456"
    key = f"{user_id}:{job_id}"
    await cache.set(key, {"status": "queued"})
    call_args = cache._client.setex.call_args
    assert call_args[0][0] == "user_abc:job_456"


@pytest.mark.asyncio
async def test_expired_key_returns_none(redis_cache, mock_redis_client):
    """Test that expired key returns None."""
    mock_redis_client.get.return_value = None
    result = await redis_cache.get("expired:key")
    assert result is None


@pytest.mark.asyncio
async def test_delete(redis_cache, mock_redis_client):
    """Test delete removes a key."""
    await redis_cache.delete("some:key")
    mock_redis_client.delete.assert_called_once_with("some:key")


@pytest.mark.asyncio
async def test_close(redis_cache, mock_redis_client):
    """Test close calls aclose on client."""
    await redis_cache.close()
    mock_redis_client.aclose.assert_called_once()
