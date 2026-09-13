from pathlib import Path

from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from arboria.app.auth import CSRF_COOKIE_NAME, CSRF_HEADER_NAME, configure_password
from arboria.app.server import create_app


def configure_auth(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("ARBORIA_DATA_DIR", str(tmp_path))
    configure_password("correct horse battery staple", tmp_path)


def login(client: TestClient) -> str:
    accepted = client.post(
        "/api/v1/auth/login", json={"password": "correct horse battery staple"}
    )
    assert accepted.status_code == 200
    csrf = accepted.cookies[CSRF_COOKIE_NAME]
    assert isinstance(csrf, str)
    return csrf


def test_plants_list_reports_starter_nursery(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        login(client)
        payload = client.get("/api/v1/plants").json()

    assert payload["nursery"]["plant_count"] == 2
    assert payload["nursery"]["organ_count"] == 6
    assert len(payload["plants"]) == 2
    assert payload["plants"][0]["plant_id"] == 1
    assert payload["plants"][0]["organ_count"] == 3


def test_plant_detail_requires_existing_plant(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        login(client)
        found = client.get("/api/v1/plants/1")
        missing = client.get("/api/v1/plants/999")

    assert found.status_code == 200
    assert found.json()["plant_id"] == 1
    assert len(found.json()["organs"]) == 3
    assert missing.status_code == 404


def test_checkpoint_and_restore_preserve_nursery(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        csrf = login(client)
        before = client.get("/api/v1/plants").json()
        saved = client.post(
            "/api/v1/saves/named",
            json={"name": "nursery"},
            headers={CSRF_HEADER_NAME: csrf},
        ).json()
        restored = client.post(
            "/api/v1/saves/restore",
            json={"name": "nursery"},
            headers={CSRF_HEADER_NAME: csrf},
        )
        after = client.get("/api/v1/plants").json()

    assert saved["snapshot"]["name"] == "nursery"
    assert restored.status_code == 200
    assert after["nursery"]["plant_count"] == before["nursery"]["plant_count"]
    assert after["nursery"]["organ_count"] == before["nursery"]["organ_count"]
    assert after["plants"][0]["stem_length_m"] >= before["plants"][0]["stem_length_m"]
