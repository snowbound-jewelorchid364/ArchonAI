from __future__ import annotations
import pytest
from unittest.mock import patch
from starlette.testclient import TestClient
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware import Middleware

from api.middleware.auth import AuthMiddleware, AuthError
from api.schemas.auth import CurrentUser


async def protected_endpoint(request: Request):
    user = getattr(request.state, "user", None)
    if user:
        return JSONResponse({"user_id": user.user_id, "email": user.email, "plan": user.plan})
    return JSONResponse({"user_id": None}, status_code=401)


app = Starlette(
    routes=[
        Route("/health", lambda r: JSONResponse({"status": "ok"})),
        Route("/protected", protected_endpoint),
        Route("/docs", lambda r: JSONResponse({"docs": True})),
    ],
    middleware=[Middleware(AuthMiddleware)],
)

client = TestClient(app, raise_server_exceptions=False)


class TestAuthExemptPaths:
    def test_health_no_auth(self):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_docs_no_auth(self):
        resp = client.get("/docs")
        assert resp.status_code == 200


class TestAuthMissingToken:
    def test_no_header_user_none(self):
        resp = client.get("/protected")
        assert resp.status_code == 401
        assert resp.json()["user_id"] is None

    def test_empty_bearer(self):
        resp = client.get("/protected", headers={"Authorization": "Bearer "})
        assert resp.status_code == 401


class TestAuthValidToken:
    @patch("api.middleware.auth.AuthMiddleware._verify_clerk_token")
    def test_valid_token(self, mock_verify):
        mock_verify.return_value = CurrentUser(user_id="u_1", email="a@b.com", plan="pro")
        resp = client.get("/protected", headers={"Authorization": "Bearer good-token"})
        assert resp.status_code == 200
        assert resp.json()["user_id"] == "u_1"
        assert resp.json()["plan"] == "pro"


class TestAuthExpiredToken:
    @patch("api.middleware.auth.AuthMiddleware._verify_clerk_token")
    def test_expired_returns_401(self, mock_verify):
        mock_verify.side_effect = AuthError("Token expired")
        resp = client.get("/protected", headers={"Authorization": "Bearer expired"})
        assert resp.status_code == 401
        assert "Token expired" in resp.json()["detail"]


class TestAuthInvalidToken:
    @patch("api.middleware.auth.AuthMiddleware._verify_clerk_token")
    def test_clerk_rejects(self, mock_verify):
        mock_verify.side_effect = AuthError("Clerk verification failed: 401")
        resp = client.get("/protected", headers={"Authorization": "Bearer invalid"})
        assert resp.status_code == 401

    @patch("api.middleware.auth.AuthMiddleware._verify_clerk_token")
    def test_clerk_down(self, mock_verify):
        mock_verify.side_effect = AuthError("Clerk verification failed: 500")
        resp = client.get("/protected", headers={"Authorization": "Bearer any"})
        assert resp.status_code == 401
