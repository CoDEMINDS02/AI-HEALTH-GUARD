from app.core.constants import DEFAULT_LIMITATIONS_TEXT, DISCLAIMER_TEXT
from app.schemas.analysis import AnalysisResultSchema
from app.schemas.reports import ReportFindings
from app.services.ai.base import AIProvider


FOLLOW_UP_RULES: list[tuple[tuple[str, ...], str]] = [
    (("fever", "temperature", "pyrexia"), "How high has your fever been, if you have measured it?"),
    (("cough",), "Is your cough dry, or are you bringing up phlegm?"),
    (("headache",), "Did the headache start suddenly or gradually, and where is it located?"),
    (("dizzy", "dizziness", "lightheaded"), "Does the dizziness happen mainly when standing up, or is it constant?"),
    (("chest pain", "chest pressure"), "Is the chest pain present right now, and does it spread to your arm, jaw, or back?"),
    (("shortness of breath", "breathless", "breathing"), "Are you having any difficulty breathing while resting?"),
    (("vomit", "nausea"), "Have you been able to keep fluids down?"),
    (("rash",), "Has the rash spread or changed in appearance recently?"),
    (("throat", "swallow"), "Do you have difficulty swallowing or breathing through your mouth?"),
    (("diarrhea", "loose motion"), "How many episodes of diarrhea have you had in the last 24 hours?"),
    (("pain",), "On a scale of 1-10, has the pain changed since it started?"),
    (("weak", "fatigue", "tired"), "Is the weakness affecting your ability to walk or do daily activities?"),
]

GENERIC_TAIL_QUESTIONS = [
    "Have your symptoms been getting better, worse, or staying the same?",
    "Are you currently taking any medication for these symptoms?",
]

CONCERN_RULES: list[tuple[tuple[str, ...], str, str]] = [
    (
        ("fever",),
        "Febrile illness (cause undetermined)",
        "Fever may be associated with common infections. If it persists beyond 3 days or rises above 39°C, it could warrant further evaluation.",
    ),
    (
        ("fever", "cough"),
        "Respiratory tract infection (possibility)",
        "Fever with cough may be associated with a viral respiratory infection. Persistent high fever, chest pain, or breathing difficulty could warrant further evaluation.",
    ),
    (
        ("fever", "sore throat"),
        "Upper respiratory / throat infection (possibility)",
        "This combination may be associated with a throat or upper respiratory infection.",
    ),
    (
        ("headache",),
        "Tension-type headache (possibility)",
        "Headache may be associated with tension, dehydration, screen strain, or lack of sleep. A sudden, severe headache could warrant urgent evaluation.",
    ),
    (
        ("headache", "dizzy"),
        "Headache with dizziness (possibilities include dehydration or inner-ear causes)",
        "This combination may be associated with dehydration, low blood sugar, or vestibular causes. Persistence could warrant further evaluation.",
    ),
    (
        ("cough",),
        "Cough (upper airway or chest related, possibility)",
        "A persistent cough beyond two weeks could warrant further evaluation.",
    ),
    (
        ("stomach", "abdominal", "nausea", "vomit", "diarrhea"),
        "Gastrointestinal irritation (possibility)",
        "These symptoms may be associated with dietary causes or a mild infection. Dehydration is worth monitoring.",
    ),
]


class DemoAIProvider(AIProvider):
    """Deterministic offline provider producing clearly synthetic, schema-valid output."""

    name = "demo"

    def generate_follow_up_questions(self, symptom_context: dict) -> list[str]:
        text = self._context_text(symptom_context)
        questions = [q for keywords, q in FOLLOW_UP_RULES if any(k in text for k in keywords)]
        for generic in GENERIC_TAIL_QUESTIONS:
            if len(questions) >= 4:
                break
            if generic not in questions:
                questions.append(generic)
        return questions[: max(2, min(6, len(questions)))] or list(GENERIC_TAIL_QUESTIONS)[:2]

    def analyze_health_information(self, payload: dict) -> AnalysisResultSchema:
        profile = payload.get("health_profile") or {}
        symptoms = payload.get("symptoms") or {}
        answers = payload.get("follow_up_answers") or []
        report = payload.get("medical_report_findings")

        all_symptoms = list(symptoms.get("primary_symptoms") or []) + list(
            symptoms.get("additional_symptoms") or []
        )
        description = str(symptoms.get("description") or "")
        severity = int(symptoms.get("severity") or 5)
        duration = str(symptoms.get("duration_text") or "an unstated duration")
        onset = str(symptoms.get("onset") or "unspecified")
        text = " ".join([description.lower()] + [str(s).lower() for s in all_symptoms])

        concerns = [
            {"title": title, "note": note}
            for keywords, title, note in CONCERN_RULES
            if sum(1 for k in keywords if k in text) >= min(2, len(keywords))
        ]
        if not concerns:
            concerns = [{
                "title": "Non-specific presentation",
                "note": "The reported symptoms alone do not point to a specific cause. Monitoring and professional review are sensible if symptoms persist or worsen.",
            }]

        risk_level = "LOW"
        if severity >= 8 or onset == "sudden" and severity >= 7:
            risk_level = "HIGH"
        elif severity >= 5 or duration_contains_weeks(duration):
            risk_level = "MODERATE"

        article = "an" if onset[:1].lower() in "aeiou" else "a"
        duration_display = duration if any(c.isalpha() for c in duration) else f"{duration} day(s)"
        observations = [
            f"Reported severity is {severity}/10 with {article} {onset} onset over {duration_display}.",
            f"{len(answers)} follow-up answer(s) were included in this assessment." if answers
            else "No follow-up answers were provided; the assessment relies on initial symptom data only.",
        ]
        if report:
            findings_count = len((report.get("findings") or []))
            observations.append(
                f"A medical report was attached with {findings_count} extracted value(s); see report findings."
            )

        next_steps = build_next_steps(risk_level)

        summary = (
            f"[DEMO OUTPUT - synthetic analysis] You reported {', '.join(all_symptoms[:6]) or 'symptoms'} "
            f"for {duration} with severity {severity}/10 ({onset} onset). "
            f"This preliminary summary only restates and organizes what you entered; it is not a diagnosis."
        )

        return AnalysisResultSchema(
            summary=summary,
            symptoms=all_symptoms,
            observations=observations,
            possible_concerns=[f"{c['title']}: {c['note']}" for c in concerns],
            risk_level=risk_level,
            red_flags=[],
            recommended_next_steps=next_steps,
            questions_for_doctor=[
                "Could my symptoms be related to any of my existing conditions or medications?",
                "What warning signs should prompt me to seek care sooner?",
                "Which tests, if any, would help clarify the cause?",
                "How long should these symptoms typically last before re-evaluation?",
            ],
            limitations=DEFAULT_LIMITATIONS_TEXT + " DEMO MODE: this response is synthetic.",
            disclaimer=DISCLAIMER_TEXT,
        )

    def explain_medical_report(self, report_text: str, findings: ReportFindings | None) -> str:
        if not findings or not findings.findings:
            return (
                "[DEMO OUTPUT] No structured values could be extracted from this report, so no "
                "explanation can be offered. Please review the document with a healthcare professional."
            )
        flagged = [f for f in findings.findings if f.flag in ("high", "low", "abnormal")]
        lines = ["[DEMO OUTPUT] Plain-language walkthrough of extracted values:"]
        for finding in flagged:
            direction = "above" if finding.flag == "high" else "below" if finding.flag == "low" else "outside"
            lines.append(
                f"- {finding.name}: {finding.value}{(' ' + finding.unit) if finding.unit else ''} is "
                f"{direction} the typical range ({finding.reference_range}). This could warrant discussion "
                f"with a healthcare professional."
            )
        normal_count = len(findings.findings) - len(flagged)
        if normal_count:
            lines.append(f"- {normal_count} value(s) fall within their typical ranges.")
        lines.append("Share the full report with a healthcare professional for interpretation.")
        return "\n".join(lines)

    @staticmethod
    def _context_text(context: dict) -> str:
        parts = [
            str(context.get("description") or ""),
            *[str(s) for s in context.get("primary_symptoms") or []],
            *[str(s) for s in context.get("additional_symptoms") or []],
        ]
        return " ".join(parts).lower()


def duration_contains_weeks(duration_text: str) -> bool:
    lowered = duration_text.lower()
    return "week" in lowered or "month" in lowered


def build_next_steps(risk_level: str) -> list[str]:
    steps = [
        "Monitor your symptoms and note any changes.",
        "Stay hydrated and get adequate rest.",
    ]
    if risk_level == "MODERATE":
        steps.append("Consider scheduling a consultation with a healthcare professional if symptoms persist beyond a few days.")
    if risk_level == "HIGH":
        steps.append("Seek medical attention promptly for proper evaluation.")
    steps.append("Use the generated question list when speaking with a healthcare professional.")
    return steps
