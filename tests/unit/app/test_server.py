from pathlib import Path

from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from arboria.app.auth import COOKIE_NAME, configure_password, password_file, sessions_file
from arboria.app.server import create_app


def configure_auth(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("ARBORIA_DATA_DIR", str(tmp_path))
    configure_password("correct horse battery staple", tmp_path)


def test_health_reports_current_implementation_scope(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["phase"] == "r1-auth-baseline"
    assert payload["implemented"]["server"] is True
    assert payload["implemented"]["authentication"] is True
    assert payload["implemented"]["simulation"] is False
    assert payload["implemented"]["persistence"] is False


def test_api_health_matches_plain_health(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    configure_auth(monkeypatch, tmp_path)
    client = TestClient(create_app())

    assert client.get("/api/v1/health").json() == client.get("/health").json()


def test_root_requires_login(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    configure_auth(monkeypatch, tmp_path)
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert "Shared password required" in response.text


def test_login_status_and_logout(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    configure_auth(monkeypatch, tmp_path)
    client = TestClient(create_app())

    assert client.get("/api/v1/auth/status").json() == {"authenticated": False}
    rejected = client.post("/api/v1/auth/login", json={"password": "wrong password"})
    assert rejected.status_code == 401

    accepted = client.post(
        "/api/v1/auth/login", json={"password": "correct horse battery staple"}
    )
    assert accepted.status_code == 200
    assert accepted.json()["authenticated"] is True
    assert COOKIE_NAME in accepted.cookies
    assert sessions_file(tmp_path).is_file()
    assert client.get("/api/v1/auth/status").json() == {"authenticated": True}

    logged_out = client.post("/api/v1/auth/logout")
    assert logged_out.status_code == 200
    assert client.get("/api/v1/auth/status").json() == {"authenticated": False}


def test_form_login_redirects_to_root(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    configure_auth(monkeypatch, tmp_path)
    client = TestClient(create_app())

    response = client.post(
        "/api/v1/auth/login",
        data={"password": "correct horse battery staple"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert COOKIE_NAME in response.cookies


def test_password_hash_stays_private(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    configure_auth(monkeypatch, tmp_path)

    stored = password_file(tmp_path).read_text(encoding="utf-8")
    assert "correct horse battery staple" not in stored
    assert "pbkdf2_sha256" in stored
