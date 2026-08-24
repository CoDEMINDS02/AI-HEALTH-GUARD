import pytest
from pydantic import ValidationError

from app.schemas.analysis import AnalysisResultSchema
from app.schemas.health_profile import HealthProfileCreate
from app.schemas.symptoms import SymptomCreate


class TestHealthProfileValidation:
    def test_valid_profile(self):
        profile = HealthProfileCreate(age=42, sex="female", conditions=["asthma"])
        assert profile.age == 42
        assert profile.conditions == ["asthma"]

    def test_age_out_of_range_rejected(self):
        with pytest.raises(ValidationError):
            HealthProfileCreate(age=-1, sex="male")
        with pytest.raises(ValidationError):
            HealthProfileCreate(age=150, sex="male")

    def test_invalid_sex_rejected(self):
        with pytest.raises(ValidationError):
            HealthProfileCreate(age=30, sex="dragon")


class TestSymptomValidation:
    def base_payload(self, **overrides):
        payload = {
            "session_id": "a" * 32,
            "primary_symptoms": ["fever"],
            "description": "",
            "duration_text": "3 days",
            "severity": 5,
            "onset": "gradual",
            "additional_symptoms": [],
        }
        payload.update(overrides)
        return payload

    def test_csv_string_is_split_into_list(self):
        data = SymptomCreate.model_validate(self.base_payload(primary_symptoms="fever, cough, chills"))
        assert data.primary_symptoms == ["fever", "cough", "chills"]

    def test_severity_bounds(self):
        with pytest.raises(ValidationError):
            SymptomCreate.model_validate(self.base_payload(severity=0))
        with pytest.raises(ValidationError):
            SymptomCreate.model_validate(self.base_payload(severity=11))

    def test_empty_primary_symptom_rejected(self):
        with pytest.raises(ValidationError):
            SymptomCreate.model_validate(self.base_payload(primary_symptoms=["  "]))

    def test_invalid_onset_rejected(self):
        with pytest.raises(ValidationError):
            SymptomCreate.model_validate(self.base_payload(onset="yesterday"))


class TestAnalysisResultSchema:
    def valid_data(self, **overrides):
        data = {
            "summary": "User reports fever for 2 days.",
            "symptoms": ["fever"],
            "observations": ["Severity reported as moderate."],
            "possible_concerns": ["Viral infection (possibility)"],
            "risk_level": "MODERATE",
            "red_flags": [],
            "recommended_next_steps": ["Monitor symptoms."],
            "questions_for_doctor": ["How long should a fever last?"],
            "limitations": "",
            "disclaimer": "",
        }
        data.update(overrides)
        return data

    def test_defaults_are_filled(self):
        result = AnalysisResultSchema.model_validate(self.valid_data())
        assert result.limitations
        assert result.disclaimer.startswith("AI HealthGuard provides")

    def test_missing_summary_rejected(self):
        data = self.valid_data()
        del data["summary"]
        with pytest.raises(ValidationError):
            AnalysisResultSchema.model_validate(data)

    def test_invalid_risk_level_rejected(self):
        with pytest.raises(ValidationError):
            AnalysisResultSchema.model_validate(self.valid_data(risk_level="EXTREME"))

    def test_string_fields_coerced_to_lists(self):
        result = AnalysisResultSchema.model_validate(self.valid_data(observations="one observation"))
        assert result.observations == ["one observation"]

    def test_concern_dicts_coerced_to_strings(self):
        concerns = [{"title": "Viral infection", "note": "possible"}]
        result = AnalysisResultSchema.model_validate(self.valid_data(possible_concerns=concerns))
        assert result.possible_concerns == ["Viral infection"]
