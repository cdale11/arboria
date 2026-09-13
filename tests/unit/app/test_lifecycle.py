from pathlib import Path
from uuid import uuid4

import pytest
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


def command(
    world: dict[str, object], kind: str, payload: dict[str, object]
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "command_id": str(uuid4()),
        "world_id": world["world_id"],
        "timeline_id": world["timeline_id"],
        "request_epoch": world["request_epoch"],
        "kind": kind,
        "payload": payload,
    }


def test_pause_freezes_ticks_but_commands_still_apply(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        csrf = login(client)
        paused = client.post("/api/v1/clock/pause", headers={CSRF_HEADER_NAME: csrf})
        assert paused.json()["paused"] is True
        frozen = client.get("/api/v1/world").json()["sim_tick"]
        assert client.get("/api/v1/world").json()["sim_tick"] == frozen

        world = client.get("/api/v1/world").json()
        watered = client.post(
            "/api/v1/commands",
            json=command(world, "nursery.water", {"plant_id": 1, "water_kg": 0.02}),
            headers={CSRF_HEADER_NAME: csrf},
        )
        assert watered.json()["status"] == "applied"
        bought = client.post(
            "/api/v1/commands",
            json=command(
                client.get("/api/v1/world").json(),
                "shop.buy_water",
                {"water_kg": 0.5},
            ),
            headers={CSRF_HEADER_NAME: csrf},
        )
        assert bought.json()["status"] == "applied"

        after = client.get("/api/v1/plants").json()
        assert after["nursery"]["reservoir_kg"] == pytest.approx(2.0 - 0.02 + 0.5)
        assert after["nursery"]["cash_minor"] == 20000 - 100
        assert after["plants"][0]["zone_water_kg"] > 0.12
        assert client.get("/api/v1/world").json()["sim_tick"] == frozen


def test_save_restore_and_speed_stay_serviceable_while_paused(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        csrf = login(client)
        assert (
            client.post("/api/v1/clock/pause", headers={CSRF_HEADER_NAME: csrf}).status_code
            == 200
        )
        frozen = client.get("/api/v1/world").json()["sim_tick"]

        checkpoint = client.post(
            "/api/v1/saves/checkpoint", headers={CSRF_HEADER_NAME: csrf}
        )
        assert checkpoint.status_code == 200
        named = client.post(
            "/api/v1/saves/named",
            json={"name": "paused"},
            headers={CSRF_HEADER_NAME: csrf},
        )
        assert named.status_code == 200

        world = client.get("/api/v1/world").json()
        bought = client.post(
            "/api/v1/commands",
            json=command(world, "shop.buy_plant", {"species_id": "crassula_ovata"}),
            headers={CSRF_HEADER_NAME: csrf},
        )
        assert bought.json()["status"] == "applied"
        assert len(client.get("/api/v1/plants").json()["plants"]) == 3

        restored = client.post(
            "/api/v1/saves/restore",
            json={"name": "paused"},
            headers={CSRF_HEADER_NAME: csrf},
        )
        assert restored.status_code == 200
        settled = client.get("/api/v1/plants").json()
        assert [plant["plant_id"] for plant in settled["plants"]] == [1, 2]
        assert client.get("/api/v1/world").json()["sim_tick"] == frozen
        assert client.get("/api/v1/clock").json()["paused"] is True

        changed = client.post(
            "/api/v1/clock/speed", json={"speed": 12.0}, headers={CSRF_HEADER_NAME: csrf}
        )
        assert changed.json()["speed"] == 12.0
        resumed = client.post("/api/v1/clock/resume", headers={CSRF_HEADER_NAME: csrf})
        assert resumed.json()["paused"] is False
        assert resumed.json()["speed"] == 12.0


def test_paused_save_survives_restart_with_nursery(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        csrf = login(client)
        client.post("/api/v1/clock/pause", headers={CSRF_HEADER_NAME: csrf})
        before = client.get("/api/v1/plants").json()
        saved = client.post(
            "/api/v1/saves/named",
            json={"name": "paused-restart"},
            headers={CSRF_HEADER_NAME: csrf},
        )
        assert saved.status_code == 200

    with TestClient(create_app()) as restarted:
        login(restarted)
        after = restarted.get("/api/v1/plants").json()
        clock = restarted.get("/api/v1/clock").json()

    assert clock["paused"] is True
    assert after["nursery"]["plant_count"] == before["nursery"]["plant_count"]
    assert after["nursery"]["cash_minor"] == before["nursery"]["cash_minor"]
    assert after["nursery"]["species_ids"] == before["nursery"]["species_ids"]
