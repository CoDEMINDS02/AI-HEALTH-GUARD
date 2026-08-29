import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.errors import register_exception_handlers
from app.api.routes import analyses, follow_up, health, profiles, reports, symptoms
from app.core.config import get_settings
from app.core.constants import DEMO_NOTICE_TEXT
from app.core.logging import get_logger, setup_logging
from app.database.session import init_db


def _cors_origins() -> list[str]:
    raw = os.environ.get("CORS_ORIGINS", "") or get_settings().cors_origins
    return [o.strip() for o in raw.split(",") if o.strip()]


# Regex that matches any https://*.vercel.app subdomain so the Vercel frontend
# is always allowed regardless of which preview/production URL is used.
_VERCEL_ORIGIN_REGEX = r"https://[a-zA-Z0-9\-]+(\.vercel\.app)"

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging()
    init_db()
    if settings.is_demo_mode:
        logger.warning("Starting in DEMO MODE. %s", DEMO_NOTICE_TEXT)
    else:
        logger.info("AI provider: %s (model: %s)", settings.ai_provider, settings.ai_model)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Preliminary health analysis assistant prototype. Not a medical device.",
        lifespan=lifespan,
    )

    # Always allow vercel.app origins via regex so the frontend works without
    # requiring CORS_ORIGINS to be set. Explicit origins are added on top.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_origin_regex=_VERCEL_ORIGIN_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(profiles.router)
    app.include_router(symptoms.router)
    app.include_router(follow_up.router)
    app.include_router(reports.router)
    app.include_router(analyses.router)

    register_exception_handlers(app)
    return app


app = create_app()
