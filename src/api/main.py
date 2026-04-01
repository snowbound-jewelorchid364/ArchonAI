from __future__ import annotations
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from .routes import health, reviews, jobs, packages, webhooks, billing, share, feedback, history, chat, inputs, intake, memory, health_score, connectors
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

    # All versioned routes live under /api/v1.
    # Routers that carry their own prefix (share, feedback, history) are included
    # WITHOUT an extra prefix here to avoid double-prefixing.
    # Routers with no built-in prefix receive one here.
    api_v1 = APIRouter(prefix="/api/v1")
    api_v1.include_router(health.router)
    api_v1.include_router(reviews.router,  prefix="/reviews",  tags=["reviews"])
    api_v1.include_router(jobs.router,     prefix="/jobs",     tags=["jobs"])
    api_v1.include_router(packages.router, prefix="/packages", tags=["packages"])
    api_v1.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
    api_v1.include_router(billing.router,  prefix="/billing",  tags=["billing"])
    api_v1.include_router(share.router)      # has own prefix="/share"
    api_v1.include_router(feedback.router)   # has own prefix="/reviews/{review_id}/feedback"
    api_v1.include_router(history.router)    # has own prefix="/reviews/history"
    api_v1.include_router(chat.router)       # has own prefix="/reviews/{review_id}/chat"
    api_v1.include_router(inputs.router)     # has own prefix="/reviews/{review_id}/inputs"
    api_v1.include_router(intake.router, prefix="/intake", tags=["intake"])
    api_v1.include_router(memory.router)           # has own prefix="/memory"
    api_v1.include_router(health_score.router)     # has own prefix="/health-score"
    api_v1.include_router(connectors.router)       # has own prefix="/connectors"

    app.include_router(api_v1)

    return app


app = create_app()



