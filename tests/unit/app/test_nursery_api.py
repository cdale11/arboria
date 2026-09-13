from pathlib import Path
from uuid import uuid4

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
    assert payload["nursery"]["reservoir_kg"] == 2.0
    assert payload["nursery"]["dead_plant_count"] == 0
    assert payload["nursery"]["zone_nitrogen_kg"] > 0.0
    assert payload["nursery"]["species_ids"] == [
        "ocimum_basilicum",
        "quercus_robur",
    ]
    assert len(payload["plants"]) == 2
    assert payload["plants"][0]["plant_id"] == 1
    assert payload["plants"][0]["species_id"] == "ocimum_basilicum"
    assert payload["plants"][0]["site_id"] == "greenhouse"
    assert payload["plants"][1]["species_id"] == "quercus_robur"
    assert payload["plants"][1]["site_id"] == "outdoor"
    assert len(payload["plants"]) == 2
    assert payload["plants"][0]["plant_id"] == 1
    assert payload["plants"][0]["organ_count"] == 3
    assert payload["plants"][0]["zone_water_kg"] > 0.0
    assert payload["plants"][0]["alive"] is True
    assert payload["plants"][0]["damage_fraction"] == 0.0
    assert payload["plants"][0]["nutrient_stress_factor"] > 0.0
    assert payload["plants"][0]["zone_nitrogen_kg"] > 0.0


def test_baseline_companion_runs_validated_care_action(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        csrf = login(client)
        configured = client.post(
            "/api/v1/companion",
            json={"enabled": True, "water_threshold": 1.0, "max_actions_per_tick": 1},
            headers={CSRF_HEADER_NAME: csrf},
        )
        ran = client.post(
            "/api/v1/companion/run",
            json={},
            headers={CSRF_HEADER_NAME: csrf},
        )

    assert configured.status_code == 200
    assert configured.json()["enabled"] is True
    assert ran.status_code == 200
    assert ran.json()["companion"]["actions_proposed"] == 1
    assert ran.json()["companion"]["actions_applied"] == 1
    assert ran.json()["receipts"][0]["actor"] == "companion"
    assert ran.json()["receipts"][0]["kind"] == "nursery.water"


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
    assert found.json()["alive"] is True
    assert found.json()["nutrient_stress_factor"] > 0.0
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
    assert after["nursery"]["zone_nitrogen_kg"] <= before["nursery"]["zone_nitrogen_kg"]
    assert after["plants"][0]["stem_length_m"] >= before["plants"][0]["stem_length_m"]
    assert after["plants"][0]["alive"] is True


def command(world: dict[str, object], kind: str, payload: dict[str, object]) -> dict[str, object]:
    return {
        "schema_version": 1,
        "command_id": str(uuid4()),
        "world_id": world["world_id"],
        "timeline_id": world["timeline_id"],
        "request_epoch": world["request_epoch"],
        "kind": kind,
        "payload": payload,
    }


def test_water_command_moves_reservoir_to_zone(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        csrf = login(client)
        world = client.get("/api/v1/world").json()
        before = client.get("/api/v1/plants").json()
        response = client.post(
            "/api/v1/commands",
            json=command(world, "nursery.water", {"plant_id": 1, "water_kg": 0.02}),
            headers={CSRF_HEADER_NAME: csrf},
        )
        after = client.get("/api/v1/plants").json()

    assert response.status_code == 200
    assert response.json()["status"] == "applied"
    assert after["plants"][0]["zone_water_kg"] >= before["plants"][0]["zone_water_kg"]
    assert after["nursery"]["reservoir_kg"] <= before["nursery"]["reservoir_kg"]


def test_water_command_rejects_unknown_plant(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        csrf = login(client)
        world = client.get("/api/v1/world").json()
        response = client.post(
            "/api/v1/commands",
            json=command(world, "nursery.water", {"plant_id": 999, "water_kg": 0.02}),
            headers={CSRF_HEADER_NAME: csrf},
        )

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"
