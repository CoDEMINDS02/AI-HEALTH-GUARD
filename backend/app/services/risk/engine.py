from app.core.constants import DISCLAIMER_TEXT
from app.schemas.analysis import AnalysisResultSchema
from app.services.risk.red_flags import SafetyAssessment

ESCALATION_STEP = (
    "URGENT: One or more warning signs were detected in what you described. Please seek urgent "
    "medical attention now rather than waiting."
)


def apply_safety_layer(
    analysis: AnalysisResultSchema,
    assessment: SafetyAssessment,
) -> AnalysisResultSchema:
    """Deterministically escalate the AI assessment when configured red flags are present.

    The safety layer can only raise the risk level, never lower it.
    """

    result = analysis.model_copy()

    for rule in assessment.triggered:
        flag_text = f"{rule.label} - {rule.guidance}"
        if not any(rule.label.lower() in existing.lower() for existing in result.red_flags):
            result.red_flags.append(flag_text)

    if assessment.has_red_flags:
        if result.risk_level != "HIGH":
            result.risk_level = "HIGH"
            result.safety_override = True
        if not any("urgent" in step.lower() for step in result.recommended_next_steps):
            result.recommended_next_steps.insert(0, ESCALATION_STEP)
    else:
        result.safety_override = False
        result.recommended_next_steps = [
            step for step in result.recommended_next_steps if step != ESCALATION_STEP
        ]

    if not result.disclaimer:
        result.disclaimer = DISCLAIMER_TEXT
    return result
