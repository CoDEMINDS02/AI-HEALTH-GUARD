import json

from pydantic import ValidationError

from app.core.errors import AIInvalidResponseError
from app.schemas.analysis import AnalysisResultSchema


def extract_json_object(text: str) -> dict:
    if not text or not text.strip():
        raise AIInvalidResponseError("The AI service returned an empty response.")

    candidate = text.strip()

    if candidate.startswith("```"):
        first_newline = candidate.find("\n")
        if first_newline != -1:
            candidate = candidate[first_newline + 1 :]
        closing = candidate.rfind("```")
        if closing != -1:
            candidate = candidate[:closing]
        candidate = candidate.strip()

    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    start = candidate.find("{")
    end = candidate.rfind("}")
    if start != -1 and end > start:
        try:
            parsed = json.loads(candidate[start : end + 1])
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

    raise AIInvalidResponseError()


def parse_analysis_response(raw_text: str) -> AnalysisResultSchema:
    data = extract_json_object(raw_text)
    try:
        return AnalysisResultSchema.model_validate(data)
    except ValidationError as exc:
        raise AIInvalidResponseError() from exc


def parse_follow_up_questions(raw_text: str, max_questions: int) -> list[str]:
    data = extract_json_object(raw_text)
    raw_questions = data.get("questions", [])
    if not isinstance(raw_questions, list):
        raise AIInvalidResponseError()
    questions = []
    for item in raw_questions:
        if isinstance(item, str) and item.strip():
            cleaned = item.strip()
            questions.append(cleaned[:500])
        elif isinstance(item, dict):
            text = item.get("question") or ""
            if text.strip():
                questions.append(text.strip()[:500])
    if not questions:
        raise AIInvalidResponseError()
    return questions[:max_questions]
