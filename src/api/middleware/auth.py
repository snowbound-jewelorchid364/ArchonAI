from __future__ import annotations
import logging
import httpx
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from ..schemas.auth import CurrentUser

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    EXEMPT_PATHS = {"/health", "/docs", "/openapi.json", "/webhooks/github"}

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        if request.method == "OPTIONS":
            return await call_next(request)

        token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
        if not token:
            request.state.user = None
            return await call_next(request)

        try:
            user = await self._verify_clerk_token(token)
            request.state.user = user
        except AuthError as exc:
            logger.warning("Auth failed: %s", exc)
            return JSONResponse(status_code=401, content={"detail": str(exc)})

        return await call_next(request)

    async def _verify_clerk_token(self, token: str) -> CurrentUser:
        from archon.config.settings import settings

        clerk_key = settings.clerk_secret_key
        if not clerk_key:
            # Dev mode: accept any token, mock user
            logger.debug("Clerk key not set — dev mode auth")
            return CurrentUser(user_id="dev-user", email="dev@archon.ai", plan="pro")

        # Verify JWT with Clerk Backend API
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.clerk.com/v1/sessions/verify",
                headers={
                    "Authorization": f"Bearer {clerk_key}",
                    "Content-Type": "application/json",
                },
                params={"token": token},
                timeout=10.0,
            )

        if resp.status_code != 200:
            raise AuthError(f"Clerk verification failed: {resp.status_code}")

        data = resp.json()
        user_id = data.get("user_id", "")
        if not user_id:
            raise AuthError("No user_id in Clerk response")

        # Fetch user details
        async with httpx.AsyncClient() as client:
            user_resp = await client.get(
                f"https://api.clerk.com/v1/users/{user_id}",
                headers={"Authorization": f"Bearer {clerk_key}"},
                timeout=10.0,
            )

        if user_resp.status_code != 200:
            raise AuthError(f"Clerk user fetch failed: {user_resp.status_code}")

        user_data = user_resp.json()
        email = ""
        if user_data.get("email_addresses"):
            email = user_data["email_addresses"][0].get("email_address", "")

        plan = user_data.get("public_metadata", {}).get("plan", "starter")

        return CurrentUser(user_id=user_id, email=email, plan=plan)


class AuthError(Exception):
    pass
