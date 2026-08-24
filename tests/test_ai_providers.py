import pytest

from app.core.constants import DISCLAIMER_TEXT
from app.core.errors import AIInvalidResponseError, ConfigurationError
from app.schemas.analysis import AnalysisResultSchema
from app.services.ai.demo_provider import DemoAIProvider
from app.services.ai.openai_compatible import OpenAICompatibleProvider
from app.services.ai.parsing import extract_json_object, parse_analysis_response


class TestDemoProvider:
    def setup_method(self):
        self.provider = DemoAIProvider()

    def symptom_context(self, **overrides):
        context = {
            "primary_symptoms": ["fever"],
            "additional_symptoms": ["cough"],
            "description": "fever and cough",
            "duration_text": "3 days",
            "severity": 5,
            "onset": "gradual",
            "max_questions": 4,
        }
        context.update(overrides)
        return context

    def test_follow_ups_relevant_and_capped(self):
        questions = self.provider.generate_follow_up_questions(self.symptom_context())
        assert 0 < len(questions) <= 4
        assert any("fever" in q.lower() for q in questions)
        assert any("cough" in q.lower() for q in questions)

    def test_follow_ups_generic_when_unknown_symptoms(self):
        questions = self.provider.generate_follow_up_questions(
            self.symptom_context(primary_symptoms=["toe numbness"], additional_symptoms=[])
        )
        assert len(questions) >= 2

    def test_analysis_is_schema_valid_and_labeled_demo(self):
        payload = {"health_profile": {"age": 30, "sex": "male"}, "symptoms": self.symptom_context()}
        result = self.provider.analyze_health_information(payload)
        assert isinstance(result, AnalysisResultSchema)
        assert result.summary.startswith("[DEMO OUTPUT")
        assert result.risk_level in {"LOW", "MODERATE", "HIGH"}
        assert result.disclaimer == DISCLAIMER_TEXT
        assert result.questions_for_doctor

    def test_no_definitive_diagnosis_language(self):
        payload = {"health_profile": {"age": 30, "sex": "male"}, "symptoms": self.symptom_context()}
        result = self.provider.analyze_health_information(payload)
        joined = " ".join(result.possible_concerns + [result.summary]).lower()
        assert "you have been diagnosed" not in joined

    def test_report_explanation_handles_empty_findings(self):
        text = self.provider.explain_medical_report("", None)
        assert "No structured values" in text


class TestJsonParsing:
    def test_plain_json_parses(self):
        data = extract_json_object('{"summary": "ok", "risk_level": "LOW"}')
        assert data["summary"] == "ok"

    def test_fenced_json_parses(self):
        raw = "```json\n{\"summary\": \"fenced\", \"risk_level\": \"LOW\"}\n```"
        data = extract_json_object(raw)
        assert data["summary"] == "fenced"

    def test_json_embedded_in_prose_parses(self):
        raw = 'Here is the result: {"summary": "embedded", "risk_level": "LOW"} hope this helps'
        assert extract_json_object(raw)["summary"] == "embedded"

    def test_garbage_raises_controlled_error(self):
        with pytest.raises(AIInvalidResponseError):
            extract_json_object("this is not json at all")

    def test_empty_response_raises(self):
        with pytest.raises(AIInvalidResponseError):
            extract_json_object("   ")

    def test_missing_required_field_raises(self):
        raw = '{"observations": [], "risk_level": "LOW"}'
        with pytest.raises(AIInvalidResponseError):
            parse_analysis_response(raw)


class TestOpenAICompatibleProvider:
    def make_provider(self, **env_overrides):
        from app.core.config import Settings

        settings = Settings(
            ai_provider="openai",
            ai_api_key="test-key",
            ai_base_url="http://localhost:9999/v1",
            ai_model="test-model",
            _env_file=None,
        )
        for key, value in env_overrides.items():
            setattr(settings, key, value)
        return OpenAICompatibleProvider(settings)

    def test_requires_api_key(self):
        with pytest.raises(ConfigurationError):
            self.make_provider(ai_api_key="")

    def test_requires_base_url(self):
        with pytest.raises(ConfigurationError):
            self.make_provider(ai_base_url="")

    def test_requires_model(self):
        with pytest.raises(ConfigurationError):
            self.make_provider(ai_model="")
