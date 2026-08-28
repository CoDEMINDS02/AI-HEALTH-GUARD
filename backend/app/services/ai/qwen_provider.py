from app.core.config import Settings, get_settings
from app.services.ai.openai_compatible import OpenAICompatibleProvider


class QwenProvider(OpenAICompatibleProvider):
    """Alibaba Cloud Qwen provider via the OpenAI-compatible API."""

    name = "qwen"

    DEFAULT_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

    def __init__(self, settings: Settings | None = None) -> None:
        resolved = settings or get_settings()
        if not resolved.ai_base_url:
            # Patch a copy of settings so the parent validation passes with the default URL.
            resolved = resolved.model_copy(update={"ai_base_url": self.DEFAULT_BASE_URL})
        super().__init__(resolved)