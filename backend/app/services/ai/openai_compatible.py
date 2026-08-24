import httpx

from app.core.config import Settings, get_settings
from app.core.errors import AIInvalidResponseError, AIProviderError, AITimeoutError, ConfigurationError
from app.schemas.analysis import AnalysisResultSchema
from app.schemas.reports import ReportFindings
from app.services.ai.base import AIProvider
from app.services.ai.parsing import parse_analysis_response, parse_follow_up_questions
from app.services.ai.prompts import (
    ANALYSIS_SYSTEM_PROMPT,
    FOLLOW_UP_SYSTEM_PROMPT,
    REPORT_EXPLAIN_PROMPT,
    build_analysis_user_payload,
    build_follow_up_user_payload,
)


class OpenAICompatibleProvider(AIProvider):
    """Works with any OpenAI-compatible chat/completions endpoint (OpenAI, vLLM, LM Studio,
    DashScope/Qwen-compatible gateways, etc.)."""

    name = "openai_compatible"

    def __init__(self, settings: Settings | None = None) -> None:
        settings = settings or get_settings()
        self.api_key = settings.ai_api_key
        self.base_url = settings.ai_base_url.rstrip("/")
        self.model = settings.ai_model
        self.timeout = settings.ai_timeout_seconds
        if not self.api_key:
            raise ConfigurationError(
                "AI_API_KEY is not configured. Set it in your .env file or use AI_PROVIDER=demo."
            )
        if not self.base_url:
            raise ConfigurationError("AI_BASE_URL is not configured for the OpenAI-compatible provider.")
        if not self.model:
            raise ConfigurationError("AI_MODEL is not configured for the OpenAI-compatible provider.")

    def _chat(self, system_prompt: str, user_content: str, *, json_mode: bool) -> str:
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "temperature": 0.2,
        }
        if json_mode:
            body["response_format"] = {"type": "json_object"}

        try:
            response = httpx.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=body,
                timeout=self.timeout,
            )
        except httpx.TimeoutException as exc:
            raise AITimeoutError("The AI service did not respond in time. Please try again.") from exc
        except httpx.HTTPError as exc:
            raise AIProviderError("Could not reach the AI service. Please try again later.") from exc

        if response.status_code != 200:
            raise AIProviderError(f"The AI service returned an error (HTTP {response.status_code}).")

        try:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError) as exc:
            raise AIInvalidResponseError() from exc

        if not isinstance(content, str):
            raise AIInvalidResponseError()
        return content

    def generate_follow_up_questions(self, symptom_context: dict) -> list[str]:
        raw = self._chat(FOLLOW_UP_SYSTEM_PROMPT, build_follow_up_user_payload(symptom_context), json_mode=True)
        return parse_follow_up_questions(raw, max_questions=symptom_context.get("max_questions") or 4)

    def analyze_health_information(self, payload: dict) -> AnalysisResultSchema:
        raw = self._chat(ANALYSIS_SYSTEM_PROMPT, build_analysis_user_payload(payload), json_mode=True)
        return parse_analysis_response(raw)

    def explain_medical_report(self, report_text: str, findings: ReportFindings | None) -> str:
        summary = findings.summary if findings else ""
        lines = [report_text[:4000]]
        if summary:
            lines.insert(0, f"Extracted values summary: {summary}")
        explanation = self._chat(REPORT_EXPLAIN_PROMPT, "\n".join(lines), json_mode=False)
        return explanation.strip()[:4000] or "No explanation could be generated."
