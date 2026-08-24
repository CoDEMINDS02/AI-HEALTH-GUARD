# Integrating Alibaba Cloud Qwen as the production AI provider

The application was built so Qwen integration requires no changes to routes, services, or the
frontend.

## Steps

1. **Create `backend/app/services/ai/qwen_provider.py`**

   ```python
   from app.services.ai.base import AIProvider
   from app.services.ai.openai_compatible import OpenAICompatibleProvider


   class QwenProvider(OpenAICompatibleProvider):
       """Alibaba Cloud Qwen via the DashScope OpenAI-compatible endpoint."""

       name = "qwen"

       DEFAULT_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
   ```

   DashScope exposes an OpenAI-compatible `/chat/completions`, so subclassing reuses request,
   timeout, JSON-parsing, and error handling. Override `_chat()` only if you need DashScope-specific
   parameters.

2. **Register it** in `PROVIDER_REGISTRY` (`factory.py`):

   ```python
   PROVIDER_REGISTRY = {
       "demo": DemoAIProvider,
       "openai": OpenAICompatibleProvider,
       "openai-compatible": OpenAICompatibleProvider,
       "qwen": QwenProvider,          # new
   }
   ```

3. **Configure `.env`**

   ```ini
   AI_PROVIDER=qwen
   AI_API_KEY=sk-...            # DashScope API key — never commit
   AI_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
   AI_MODEL=qwen-max            # or qwen-plus / qwen-turbo
   ```

4. **Verify**
   - `GET /api/health` should report `"provider": "qwen"`.
   - Run the full flow; confirm `source == "qwen"` on results.
   - Re-run the test suite; safety-layer tests are provider-independent.

5. **Production hardening (recommended before launch)**
   - Add response-caching and rate limiting per session/IP.
   - Log token usage and latency; add retries with backoff around `_chat()`.
   - Keep `AI_TIMEOUT_SECONDS` moderate and surface timeouts as friendly errors (already done).
   - Consider a Qwen "vision" model later to replace the OCR stub for image reports — implement it
     inside `QwenProvider.explain_medical_report` or a new method, keeping the abstraction intact.

## Why this is safe to swap

- The app depends only on the `AIProvider` interface and the Pydantic output contract.
- The deterministic safety layer runs *after* any provider, so vendor behavior can never bypass it.
- Demo mode remains available as a permanent fallback and integration test fixture.
