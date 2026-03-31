from __future__ import annotations
import logging
import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)

# In-memory fallback when Redis is unavailable
_buckets: dict[str, list[float]] = defaultdict(list)
MAX_REQUESTS = 100
WINDOW_SECONDS = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    EXEMPT_PATHS = {"/health", "/docs", "/openapi.json"}

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        user = getattr(request.state, "user", None)
        key = user.user_id if user else request.client.host if request.client else "unknown"

        if not self._allow(key):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Max 100 requests per minute."},
                headers={"Retry-After": str(WINDOW_SECONDS)},
            )

        response = await call_next(request)
        return response

    def _allow(self, key: str) -> bool:
        now = time.monotonic()
        window_start = now - WINDOW_SECONDS
        bucket = _buckets[key]
        # Prune old entries
        _buckets[key] = [t for t in bucket if t > window_start]
        if len(_buckets[key]) >= MAX_REQUESTS:
            return False
        _buckets[key].append(now)
        return True
