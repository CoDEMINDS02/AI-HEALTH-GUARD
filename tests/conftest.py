import os
import pathlib
import sys
import tempfile

BACKEND_DIR = pathlib.Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

_TMP_DIR = tempfile.mkdtemp(prefix="healthguard_test_")
os.environ["ENV_FILE"] = os.path.join(_TMP_DIR, "no-env-file.env")
os.environ["AI_PROVIDER"] = "demo"
os.environ["DATABASE_URL"] = f"sqlite:///{pathlib.Path(_TMP_DIR) / 'test.db'}".replace("\\", "/")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import create_app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def session_ids(client):
    response = client.post(
        "/api/profile",
        json={"age": 30, "sex": "male", "conditions": [], "allergies": [], "medications": []},
    )
    assert response.status_code == 201
    data = response.json()
    return {"profile_id": data["profile_id"], "session_id": data["session_id"]}


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
