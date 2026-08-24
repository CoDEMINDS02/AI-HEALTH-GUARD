from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.database.session import get_db
from app.services.ai.factory import get_ai_provider
from app.services.ai.base import AIProvider

__all__ = ["get_db", "get_settings_dep", "get_provider"]


def get_settings_dep() -> Settings:
    return get_settings()


def get_provider(settings: Settings = Depends(get_settings_dep)) -> AIProvider:
    return get_ai_provider(settings)
