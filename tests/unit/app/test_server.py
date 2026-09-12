from fastapi.testclient import TestClient

from arboria.app.server import create_app


def test_health_reports_current_implementation_scope() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["phase"] == "r1-launcher-baseline"
    assert payload["implemented"]["server"] is True
    assert payload["implemented"]["simulation"] is False
    assert payload["implemented"]["persistence"] is False


def test_api_health_matches_plain_health() -> None:
    client = TestClient(create_app())

    assert client.get("/api/v1/health").json() == client.get("/health").json()
