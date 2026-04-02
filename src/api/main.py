from __future__ import annotations
import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .middleware.auth import AuthMiddleware
from .middleware.rate_limit import RateLimitMiddleware
from .routes import (
    auth,
    billing,
    chat,
    connectors,
    cost_optimiser,
    feedback,
    health,
    health_score,
    history,
    inputs,
    intake,
    jobs,
    memory,
    packages,
    reviews,
    share,
    webhooks,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parents[1]))

    from archon.config.settings import settings
    from db.connection import create_tables, init_db, shutdown_db

    logger.info("Starting ARCHON API...")
    init_db(settings.database_url)
    await create_tables()
    logger.info("Database initialized")

    yield

    await shutdown_db()
    logger.info("ARCHON API shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title="ARCHON API",
        version="0.4.0",
        description="Autonomous AI Architecture Co-Pilot",
        docs_url="/docs",
        redoc_url=None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(AuthMiddleware)

    api_v1 = APIRouter(prefix="/api/v1")
    api_v1.include_router(health.router)
    api_v1.include_router(auth.router)
    api_v1.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
    api_v1.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
    api_v1.include_router(packages.router, prefix="/packages", tags=["packages"])
    api_v1.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
    api_v1.include_router(billing.router, prefix="/billing", tags=["billing"])
    api_v1.include_router(share.router)
    api_v1.include_router(feedback.router)
    api_v1.include_router(history.router)
    api_v1.include_router(chat.router)
    api_v1.include_router(inputs.router)
    api_v1.include_router(intake.router, prefix="/intake", tags=["intake"])
    api_v1.include_router(memory.router)
    api_v1.include_router(health_score.router)
    api_v1.include_router(connectors.router)
    api_v1.include_router(cost_optimiser.router)

    app.include_router(api_v1)
    return app


app = create_app()
