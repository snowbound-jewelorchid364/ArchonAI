from __future__ import annotations
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import health, reviews, jobs, packages, webhooks, billing, share, feedback, history
from .middleware.auth import AuthMiddleware
from .middleware.rate_limit import RateLimitMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parents[1]))

    from archon.config.settings import settings
    from db.connection import init_db, create_tables, shutdown_db

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

    app.include_router(health.router)
    app.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
    app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
    app.include_router(packages.router, prefix="/packages", tags=["packages"])
    app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
    app.include_router(billing.router, prefix="/billing", tags=["billing"])
    app.include_router(share.router, prefix="/share", tags=["share"])
    app.include_router(feedback.router, tags=["feedback"])
    app.include_router(history.router, tags=["history"])

    return app


app = create_app()
