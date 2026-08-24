from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.deps import get_settings_dep
from app.core.config import Settings

router = APIRouter(tags=["health"])


@router.get("/api/health")
def health_check(settings: Settings = Depends(get_settings_dep)) -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "provider": settings.ai_provider,
        "model": settings.ai_model or None,
        "demo_mode": settings.is_demo_mode,
        "time": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/")
def root(settings: Settings = Depends(get_settings_dep)) -> JSONResponse:
    return JSONResponse(
        {
            "app": settings.app_name,
            "version": settings.app_version,
            "demo_mode": settings.is_demo_mode,
            "docs": "/docs",
            "health": "/api/health",
        }
    )
