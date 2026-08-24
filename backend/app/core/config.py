import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "AI HealthGuard API"
    app_version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "INFO"

    database_url: str = "sqlite:///./healthguard.db"

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    ai_provider: str = "demo"
    ai_api_key: str = ""
    ai_base_url: str = ""
    ai_model: str = ""
    ai_timeout_seconds: float = 45.0
    ai_max_follow_up_questions: int = 4

    upload_max_bytes: int = 10 * 1024 * 1024

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_demo_mode(self) -> bool:
        return self.ai_provider.strip().lower() == "demo"

    @property
    def provider_label(self) -> str:
        if self.is_demo_mode:
            return "demo"
        return f"{self.ai_provider}:{self.ai_model or 'unspecified-model'}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
