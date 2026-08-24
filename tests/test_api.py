from fastapi.testclient import TestClient

from app.api.deps import get_provider
from app.core.errors import AIInvalidResponseError
from app.services.ai.base import AIProvider


def add_symptoms(client, session_id, primary=None, description="", severity=5,
                 onset="gradual", duration="2 days", additional=None):
    payload = {
        "session_id": session_id,
        "primary_symptoms": primary or ["fever"],
        "description": description,
        "duration_text": duration,
        "severity": severity,
        "onset": onset,
        "additional_symptoms": additional or [],
    }
    return client.post("/api/symptoms", json=payload)


class TestHealthEndpoint:
    def test_health_ok(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["demo_mode"] is True
        assert body["provider"] == "demo"

    def test_root_info(self, client):
        body = client.get("/").json()
        assert body["demo_mode"] is True


class TestProfileEndpoint:
    def test_create_profile_returns_bundle(self, client):
        response = client.post(
            "/api/profile",
            json={"age": 45, "sex": "female", "conditions": ["hypertension"], "medications": []},
        )
        assert response.status_code == 201
        body = response.json()
        assert len(body["session_id"]) >= 8
        assert body["profile_id"] > 0

    def test_invalid_profile_rejected_with_envelope(self, client):
        response = client.post("/api/profile", json={"age": 300, "sex": "female"})
        assert response.status_code == 422
        body = response.json()
        assert body["error"]["code"] == "validation_error"
        assert body["error"]["details"]

    def test_missing_profile_404(self, client):
        assert client.get("/api/profile/99999").status_code == 404


class TestSymptomsEndpoint:
    def test_submit_symptoms(self, client, session_ids):
        response = add_symptoms(client, session_ids["session_id"], primary=["fever", "cough"])
        assert response.status_code == 201
        assert response.json()["status"] == "symptoms_recorded"

    def test_unknown_session_rejected(self, client):
        payload = {
            "session_id": "z" * 32,
            "primary_symptoms": ["fever"],
            "severity": 5,
            "onset": "gradual",
        }
        assert client.post("/api/symptoms", json=payload).status_code == 404


class TestFollowUpEndpoint:
    def test_generate_and_answer_follow_ups(self, client, session_ids):
        add_symptoms(client, session_ids["session_id"], primary=["fever"])
        gen = client.post("/api/follow-up", json={"session_id": session_ids["session_id"]})
        assert gen.status_code == 200
        questions = gen.json()["questions"]
        assert 0 < len(questions) <= 4

        answers = {"session_id": session_ids["session_id"],
                   "answers": [{"question": q, "answer": "about 38.5C"} for q in questions]}
        submitted = client.post("/api/follow-up/answers", json=answers)
        assert submitted.status_code == 200

    def test_requires_symptoms_first(self, client, session_ids):
        response = client.post("/api/follow-up", json={"session_id": session_ids["session_id"]})
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "invalid_state"


def run_full_flow(client: TestClient) -> dict:
    profile = client.post(
        "/api/profile",
        json={"age": 28, "sex": "male", "conditions": [], "allergies": ["penicillin"], "medications": []},
    ).json()
    sid = profile["session_id"]
    add_symptoms(client, sid, primary=["fever", "headache"], description="fever and headache", severity=4)
    questions = client.post("/api/follow-up", json={"session_id": sid}).json()["questions"]
    client.post("/api/follow-up/answers",
                json={"session_id": sid, "answers": [{"question": q, "answer": "no"} for q in questions]})
    analyzed = client.post("/api/analyze", json={"session_id": sid})
    return analyzed.json()


class TestAnalysisFlow:
    def test_full_flow_case_1_fever_cough(self, client, session_ids):
        add_symptoms(client, session_ids["session_id"], primary=["fever"], additional=["cough"])
        client.post("/api/follow-up", json={"session_id": session_ids["session_id"]})
        result = client.post("/api/analyze", json={"session_id": session_ids["session_id"]})
        assert result.status_code == 200
        body = result.json()
        assert body["risk_level"] in {"LOW", "MODERATE"}
        assert body["source"] == "demo"
        assert body["disclaimer"].startswith("AI HealthGuard provides")
        assert body["possible_concerns"]

    def test_full_flow_case_2_headache_dizziness(self, client, session_ids):
        add_symptoms(client, session_ids["session_id"], primary=["headache"], additional=["dizziness"],
                     description="dull headache with mild dizziness when standing")
        result = client.post("/api/analyze", json={"session_id": session_ids["session_id"]}).json()
        assert result["risk_level"] != "HIGH"
        assert any("dizz" in s.lower() for s in result["symptoms"] + [result["summary"]])

    def test_case_3_red_flag_overrides_ai_risk(self, client, session_ids):
        add_symptoms(
            client,
            session_ids["session_id"],
            primary=["chest pain"],
            additional=["difficulty breathing"],
            description="crushing chest pain radiating to my left arm with severe difficulty breathing",
            severity=5,
            onset="sudden",
        )
        result = client.post("/api/analyze", json={"session_id": session_ids["session_id"]}).json()
        assert result["risk_level"] == "HIGH"
        assert result["red_flags"]
        assert result["safety_override"] is True
        assert any("urgent" in step.lower() for step in result["recommended_next_steps"])

    def test_get_analysis_by_id(self, client):
        analysis = run_full_flow(client)
        fetched = client.get(f"/api/analyses/{analysis['id']}")
        assert fetched.status_code == 200
        assert fetched.json()["session_id"] == analysis["session_id"]

    def test_list_analyses(self, client):
        run_full_flow(client)
        listing = client.get("/api/analyses")
        assert listing.status_code == 200
        assert isinstance(listing.json(), list)

    def test_missing_analysis_404(self, client):
        assert client.get("/api/analyses/99999").status_code == 404

    def test_analyze_without_symptoms_rejected(self, client, session_ids):
        response = client.post("/api/analyze", json={"session_id": session_ids["session_id"]})
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "invalid_state"


class BrokenAIProvider(AIProvider):
    name = "broken"

    def generate_follow_up_questions(self, symptom_context):
        return ["Is it worse at night?"]

    def analyze_health_information(self, payload):
        raise AIInvalidResponseError()

    def explain_medical_report(self, report_text, findings):
        return ""


class TestMalformedAIResponse:
    def test_malformed_ai_output_returns_controlled_error(self, client, session_ids, monkeypatch):
        app = client.app
        app.dependency_overrides[get_provider] = lambda: BrokenAIProvider()
        try:
            add_symptoms(client, session_ids["session_id"], primary=["fever"])
            response = client.post("/api/analyze", json={"session_id": session_ids["session_id"]})
        finally:
            app.dependency_overrides.pop(get_provider, None)

        assert response.status_code == 502
        body = response.json()
        assert body["error"]["code"] == "ai_invalid_response"
        assert "fever" not in str(body)
