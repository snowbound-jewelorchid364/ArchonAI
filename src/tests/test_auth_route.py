from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from api.routes.auth import router
from api.schemas.auth import CurrentUser


def _make_app(user: CurrentUser | None) -> FastAPI:
    app = FastAPI()

    @app.middleware("http")
    async def inject_user(request: Request, call_next):
        request.state.user = user
        return await call_next(request)

    app.include_router(router, prefix="/api/v1")
    return app


def test_auth_me_returns_current_user() -> None:
    app = _make_app(CurrentUser(user_id="u_1", email="dev@archon.ai", plan="pro"))
    client = TestClient(app)

    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200
    assert response.json() == {
        "user_id": "u_1",
        "email": "dev@archon.ai",
        "plan": "pro",
    }


def test_auth_me_requires_authentication() -> None:
    app = _make_app(None)
    client = TestClient(app)

    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"
