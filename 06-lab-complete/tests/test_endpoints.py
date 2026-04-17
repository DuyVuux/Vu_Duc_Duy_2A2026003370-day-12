import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["ENVIRONMENT"] = "development"
os.environ["AGENT_API_KEY"] = "test-key-for-testing"
os.environ.pop("OPENAI_API_KEY", None)

from fastapi.testclient import TestClient
from app.main import app
import app.main as current_main
from app.config import settings

# Mock initialization that usually happens in lifespan and override cached setting
current_main._is_ready = True
API_KEY = "test-key-for-testing"
settings.agent_api_key = API_KEY

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "version" in data
    assert "endpoints" in data


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "uptime_seconds" in data
    assert "timestamp" in data


def test_ready():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["ready"] is True


def test_ask_without_api_key():
    response = client.post("/ask", json={"question": "test"})
    assert response.status_code == 401


def test_ask_with_wrong_api_key():
    response = client.post(
        "/ask",
        json={"question": "test"},
        headers={"X-API-Key": "wrong-key"},
    )
    assert response.status_code == 401


def test_ask_with_valid_api_key():
    response = client.post(
        "/ask",
        json={"question": "What is Docker?"},
        headers={"X-API-Key": API_KEY},
    )
    assert response.status_code == 200
    data = response.json()
    assert "question" in data
    assert "answer" in data
    assert "model" in data
    assert "timestamp" in data


def test_ask_empty_question():
    response = client.post(
        "/ask",
        json={"question": ""},
        headers={"X-API-Key": API_KEY},
    )
    assert response.status_code == 422


def test_metrics_requires_api_key():
    response = client.get("/metrics")
    assert response.status_code == 401


def test_metrics_with_api_key():
    response = client.get(
        "/metrics",
        headers={"X-API-Key": API_KEY},
    )
    assert response.status_code == 200
    data = response.json()
    assert "daily_cost_usd" in data
    assert "budget_used_pct" in data


def test_security_headers():
    response = client.get("/health")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert "server" not in response.headers
