from types import SimpleNamespace

from fastapi.testclient import TestClient

import app.main as main
from app.config import Settings, get_settings
from app.usage import get_usage_summary, log_usage


def test_health_endpoint():
    client = TestClient(main.app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_endpoint_with_mock(monkeypatch):
    settings = Settings(
        gemini_api_key="test-key",
        app_name="CallShield",
    )
    main.app.dependency_overrides[get_settings] = lambda: settings

    def fake_generate_json(request, settings):
        return main.ChatResponse(
            answer="Do not share your OTP.",
            steps=[
                "End the call.",
                "Block the number if suspicious.",
                "Report the incident through an official channel.",
            ],
            sources=[],
            disclaimer=(
                "AI-generated guidance; not yet verified "
                "against CallShield documents."
            ),
        )

    monkeypatch.setattr(main, "generate_json", fake_generate_json)

    try:
        client = TestClient(main.app)
        response = client.post(
            "/chat",
            json={
                "message": "A caller asked me for my OTP. What should I do?"
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Do not share your OTP."
        assert len(data["steps"]) == 3
        assert data["sources"] == []
        assert data["disclaimer"]
    finally:
        main.app.dependency_overrides.clear()


def test_chat_rejects_empty_message():
    client = TestClient(main.app)

    response = client.post("/chat", json={"message": ""})

    assert response.status_code == 422


def test_stream_endpoint_with_mock(monkeypatch):
    settings = Settings(
        gemini_api_key="test-key",
        app_name="CallShield",
    )
    main.app.dependency_overrides[get_settings] = lambda: settings

    class FakeModels:
        def generate_content_stream(self, **kwargs):
            yield SimpleNamespace(text="Never share your OTP.")
            yield SimpleNamespace(text=" Report suspicious calls.")

    class FakeClient:
        models = FakeModels()

    monkeypatch.setattr(main, "create_client", lambda settings: FakeClient())

    try:
        client = TestClient(main.app)
        response = client.post(
            "/chat/stream",
            json={"message": "How do I handle a suspicious call?"},
        )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        assert "event: token" in response.text
        assert "Never share your OTP." in response.text
        assert "event: done" in response.text
    finally:
        main.app.dependency_overrides.clear()

def test_usage_logging_and_cost_calculation(tmp_path):
    log_file = tmp_path / "usage.jsonl"

    log_usage(
        log_path=str(log_file),
        model="test-model",
        prompt_tokens=1000,
        candidate_tokens=500,
        total_tokens=1500,
        input_price_per_million=0.5,
        output_price_per_million=1.0,
    )

    summary = get_usage_summary(str(log_file))

    assert summary["request_count"] == 1
    assert summary["usage_available_request_count"] == 1
    assert summary["total_prompt_tokens"] == 1000
    assert summary["total_candidate_tokens"] == 500
    assert summary["total_tokens"] == 1500
    assert summary["estimated_cost_usd"] == 0.001
    assert summary["cost_available"] is True
