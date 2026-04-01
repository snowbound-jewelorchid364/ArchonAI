from __future__ import annotations
import time
import pytest
from starlette.testclient import TestClient
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware import Middleware

from api.middleware.rate_limit import RateLimitMiddleware, _buckets, MAX_REQUESTS, WINDOW_SECONDS


async def ok_endpoint(request: Request):
    return JSONResponse({"ok": True})


app = Starlette(
    routes=[
        Route("/health", lambda r: JSONResponse({"status": "ok"})),
        Route("/test", ok_endpoint),
    ],
    middleware=[Middleware(RateLimitMiddleware)],
)

client = TestClient(app, raise_server_exceptions=False)


class TestRateLimitExempt:
    def test_health_exempt(self):
        _buckets.clear()
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_docs_exempt(self):
        _buckets.clear()
        resp = client.get("/docs")
        assert resp.status_code in (200, 404)


class TestRateLimitEnforcement:
    def test_under_limit_allowed(self):
        _buckets.clear()
        resp = client.get("/test")
        assert resp.status_code == 200

    def test_at_limit_returns_429(self):
        _buckets.clear()
        key = "testclient"
        now = time.monotonic()
        _buckets[key] = [now - i * 0.1 for i in range(MAX_REQUESTS)]
        resp = client.get("/test")
        assert resp.status_code == 429

    def test_429_has_retry_after(self):
        _buckets.clear()
        key = "testclient"
        now = time.monotonic()
        _buckets[key] = [now - i * 0.1 for i in range(MAX_REQUESTS)]
        resp = client.get("/test")
        assert resp.status_code == 429
        assert resp.headers.get("retry-after") == str(WINDOW_SECONDS)
        assert "Rate limit exceeded" in resp.json()["detail"]

    def test_expired_entries_pruned(self):
        _buckets.clear()
        key = "testclient"
        old_time = time.monotonic() - WINDOW_SECONDS - 10
        _buckets[key] = [old_time] * MAX_REQUESTS
        resp = client.get("/test")
        assert resp.status_code == 200
