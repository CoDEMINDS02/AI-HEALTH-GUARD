from app.core.config import Settings, get_settings
from app.core.errors import ConfigurationError
from app.services.ai.base import AIProvider
from app.services.ai.demo_provider import DemoAIProvider
from app.services.ai.openai_compatible import OpenAICompatibleProvider


PROVIDER_REGISTRY: dict[str, type[AIProvider]] = {
    "demo": DemoAIProvider,
    "openai": OpenAICompatibleProvider,
    "openai-compatible": OpenAICompatibleProvider,
}


def get_ai_provider(settings: Settings | None = None) -> AIProvider:
    settings = settings or get_settings()
    key = settings.ai_provider.strip().lower()
    provider_cls = PROVIDER_REGISTRY.get(key)
    if provider_cls is None:
        supported = ", ".join(sorted(PROVIDER_REGISTRY))
        raise ConfigurationError(f"Unsupported AI_PROVIDER '{key}'. Supported values: {supported}.")
    return provider_cls(settings)
