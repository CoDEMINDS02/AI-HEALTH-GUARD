from app.services.risk.engine import ESCALATION_STEP, apply_safety_layer
from app.schemas.analysis import AnalysisResultSchema
from app.services.risk.red_flags import RED_FLAG_RULES, assess_text_safety


def make_analysis(**overrides):
    data = {
        "summary": "Synthetic summary.",
        "symptoms": ["headache"],
        "observations": [],
        "possible_concerns": ["Tension headache (possibility)"],
        "risk_level": "LOW",
        "red_flags": [],
        "recommended_next_steps": ["Monitor symptoms."],
        "questions_for_doctor": ["When should I be seen?"],
    }
    data.update(overrides)
    return AnalysisResultSchema.model_validate(data)


class TestRedFlagDetection:
    def test_benign_text_has_no_flags(self):
        assessment = assess_text_safety("mild headache for two days, feeling tired")
        assert not assessment.has_red_flags

    def test_breathing_difficulty_detected(self):
        assessment = assess_text_safety("I can't breathe and my lips are turning blue")
        labels = assessment.labels
        assert "Severe difficulty breathing" in labels

    def test_crushing_chest_pain_detected(self):
        assessment = assess_text_safety("crushing chest pain radiating to my left arm")
        assert any(r.rule_id == "severe_chest_pain" for r in assessment.triggered)

    def test_fainting_detected(self):
        assessment = assess_text_safety("I passed out this morning")
        assert "Loss of consciousness / fainting" in assessment.labels

    def test_stroke_signs_detected(self):
        assessment = assess_text_safety("slurred speech and weakness on one side")
        assert "Sudden severe neurological symptoms" in assessment.labels

    def test_fever_with_stiff_neck_detected_in_any_order(self):
        assert assess_text_safety("fever since yesterday with a stiff neck").has_red_flags
        assert assess_text_safety("stiff neck and fever").has_red_flags

    def test_all_rules_have_patterns(self):
        assert len(RED_FLAG_RULES) >= 8


class TestSafetyOverride:
    def test_low_ai_risk_is_overridden_to_high(self):
        analysis = make_analysis(risk_level="LOW")
        assessment = assess_text_safety("severe difficulty breathing at rest")
        result = apply_safety_layer(analysis, assessment)
        assert result.risk_level == "HIGH"
        assert result.safety_override is True
        assert result.red_flags
        assert any("URGENT" in step for step in result.recommended_next_steps)

    def test_moderate_ai_risk_is_overridden_to_high(self):
        analysis = make_analysis(risk_level="MODERATE")
        assessment = assess_text_safety("uncontrolled bleeding that won't stop")
        result = apply_safety_layer(analysis, assessment)
        assert result.risk_level == "HIGH"
        assert result.safety_override is True

    def test_high_ai_risk_without_flags_stays_high(self):
        analysis = make_analysis(risk_level="HIGH")
        assessment = assess_text_safety("mild sore throat")
        result = apply_safety_layer(analysis, assessment)
        assert result.risk_level == "HIGH"
        assert result.safety_override is False

    def test_no_flags_leaves_low_untouched(self):
        analysis = make_analysis(risk_level="LOW")
        assessment = assess_text_safety("runny nose for one day")
        result = apply_safety_layer(analysis, assessment)
        assert result.risk_level == "LOW"
        assert result.safety_override is False
        assert ESCALATION_STEP not in result.recommended_next_steps

    def test_original_analysis_not_mutated(self):
        analysis = make_analysis(risk_level="LOW")
        assessment = assess_text_safety("seizure occurred")
        apply_safety_layer(analysis, assessment)
        assert analysis.risk_level == "LOW"
