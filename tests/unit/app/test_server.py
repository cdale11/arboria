from pathlib import Path
from typing import cast
from uuid import uuid4

from fastapi.testclient import TestClient
from pytest import MonkeyPatch
from starlette.websockets import WebSocketDisconnect

from arboria.app.auth import (
    COOKIE_NAME,
    CSRF_COOKIE_NAME,
    CSRF_HEADER_NAME,
    configure_password,
    password_file,
    sessions_file,
)
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
    assert payload["phase"] == "r1-world-metadata-baseline"
    assert payload["implemented"]["server"] is True
    assert payload["implemented"]["authentication"] is True
    assert payload["implemented"]["process_lock"] is True
    assert payload["implemented"]["world_metadata"] is True
    assert payload["implemented"]["stream_protocol"] is True
    assert payload["implemented"]["checkpoint_layout"] is True
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
    assert CSRF_COOKIE_NAME in accepted.cookies
    assert sessions_file(tmp_path).is_file()
    assert client.get("/api/v1/auth/status").json() == {"authenticated": True}

    rejected_logout = client.post("/api/v1/auth/logout")
    assert rejected_logout.status_code == 403

    logged_out = client.post(
        "/api/v1/auth/logout",
        headers={CSRF_HEADER_NAME: accepted.cookies[CSRF_COOKIE_NAME]},
    )
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
    assert CSRF_COOKIE_NAME in response.cookies


def test_cross_origin_mutations_are_rejected(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    configure_auth(monkeypatch, tmp_path)
    client = TestClient(create_app())

    response = client.post(
        "/api/v1/auth/login",
        json={"password": "correct horse battery staple"},
        headers={"Origin": "http://attacker.invalid"},
    )

    assert response.status_code == 403


def test_failed_login_rate_limit(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    configure_auth(monkeypatch, tmp_path)
    client = TestClient(create_app())

    for _ in range(5):
        response = client.post("/api/v1/auth/login", json={"password": "wrong password"})
        assert response.status_code == 401

    limited = client.post("/api/v1/auth/login", json={"password": "wrong password"})
    assert limited.status_code == 429


def test_password_hash_stays_private(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    configure_auth(monkeypatch, tmp_path)

    stored = password_file(tmp_path).read_text(encoding="utf-8")
    assert "correct horse battery staple" not in stored
    assert "pbkdf2_sha256" in stored


def login(client: TestClient) -> str:
    accepted = client.post(
        "/api/v1/auth/login", json={"password": "correct horse battery staple"}
    )
    assert accepted.status_code == 200
    csrf = accepted.cookies[CSRF_COOKIE_NAME]
    return cast(str, csrf)


def test_clock_requires_authentication(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    configure_auth(monkeypatch, tmp_path)
    client = TestClient(create_app())

    response = client.get("/api/v1/clock")

    assert response.status_code == 401


def test_clock_pause_resume_and_speed_require_csrf(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    client = TestClient(create_app())
    csrf = login(client)

    first = client.get("/api/v1/clock")
    assert first.status_code == 200
    assert first.json()["speed"] == 48.0
    assert first.json()["paused"] is False

    rejected = client.post("/api/v1/clock/pause")
    assert rejected.status_code == 403

    paused = client.post("/api/v1/clock/pause", headers={CSRF_HEADER_NAME: csrf})
    assert paused.status_code == 200
    assert paused.json()["paused"] is True

    changed = client.post(
        "/api/v1/clock/speed", json={"speed": 12.0}, headers={CSRF_HEADER_NAME: csrf}
    )
    assert changed.status_code == 200
    assert changed.json()["speed"] == 12.0

    resumed = client.post("/api/v1/clock/resume", headers={CSRF_HEADER_NAME: csrf})
    assert resumed.status_code == 200
    assert resumed.json()["paused"] is False


def test_clock_rejects_invalid_speed(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    configure_auth(monkeypatch, tmp_path)
    client = TestClient(create_app())
    csrf = login(client)

    response = client.post(
        "/api/v1/clock/speed", json={"speed": 0.0}, headers={CSRF_HEADER_NAME: csrf}
    )

    assert response.status_code == 400


def test_world_metadata_and_clock_survive_restart(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        csrf = login(client)
        world = client.get("/api/v1/world").json()
        paused = client.post("/api/v1/clock/pause", headers={CSRF_HEADER_NAME: csrf})
        assert paused.status_code == 200
        changed = client.post(
            "/api/v1/clock/speed", json={"speed": 12.0}, headers={CSRF_HEADER_NAME: csrf}
        )
        assert changed.status_code == 200

    with TestClient(create_app()) as restarted:
        login(restarted)
        restarted_world = restarted.get("/api/v1/world").json()
        restarted_clock = restarted.get("/api/v1/clock").json()

    assert restarted_world["world_id"] == world["world_id"]
    assert restarted_world["timeline_id"] != world["timeline_id"]
    assert restarted_world["schema_version"] == 1
    assert restarted_world["request_epoch"] == world["request_epoch"] + 1
    assert restarted_world["sim_tick"] >= world["sim_tick"]
    assert restarted_world["world_revision"] >= world["world_revision"]
    assert restarted_clock["paused"] is True
    assert restarted_clock["speed"] == 12.0


def test_world_loop_fields_are_reported(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        login(client)
        world = client.get("/api/v1/world").json()

    assert world["base_tick_seconds"] == 300
    assert world["sim_tick"] >= 0
    assert world["world_revision"] >= 0
    assert world["consumed_sim_time_seconds"] >= 0.0


def test_manual_checkpoint_requires_authentication(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        response = client.post("/api/v1/saves/checkpoint")

    assert response.status_code == 401


def test_manual_checkpoint_requires_csrf(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        login(client)
        response = client.post("/api/v1/saves/checkpoint")

    assert response.status_code == 403


def test_manual_checkpoint_creates_manifest_and_updates_world(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        csrf = login(client)
        response = client.post(
            "/api/v1/saves/checkpoint", headers={CSRF_HEADER_NAME: csrf}
        )
        world = client.get("/api/v1/world").json()

    payload = response.json()
    checkpoint_id = payload["checkpoint_id"]
    assert response.status_code == 200
    assert payload["status"] == "complete"
    assert (tmp_path / "checkpoints" / checkpoint_id / "manifest.json").is_file()
    assert (tmp_path / "checkpoints" / checkpoint_id / "state.json").is_file()
    assert world["active_checkpoint_id"] == checkpoint_id


def test_save_listing_requires_authentication(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        response = client.get("/api/v1/saves")

    assert response.status_code == 401


def test_named_save_requires_csrf(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        login(client)
        response = client.post("/api/v1/saves/named", json={"name": "Morning"})

    assert response.status_code == 403


def test_named_save_creates_checkpoint_and_list_entry(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        csrf = login(client)
        created = client.post(
            "/api/v1/saves/named",
            json={"name": "Morning"},
            headers={CSRF_HEADER_NAME: csrf},
        )
        listed = client.get("/api/v1/saves")

    assert created.status_code == 200
    snapshot = created.json()["snapshot"]
    assert snapshot["name"] == "Morning"
    assert snapshot["protected"] is True
    assert (tmp_path / "checkpoints" / snapshot["checkpoint_id"] / "manifest.json").is_file()
    assert listed.json()["snapshots"] == [snapshot]


def test_named_save_rejects_path_like_names(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        csrf = login(client)
        response = client.post(
            "/api/v1/saves/named",
            json={"name": "../bad"},
            headers={CSRF_HEADER_NAME: csrf},
        )

    assert response.status_code == 400


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


def test_command_endpoint_applies_clock_command_and_deduplicates_receipt(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        csrf = login(client)
        world = client.get("/api/v1/world").json()
        envelope = command(world, "clock.set_speed", {"speed": 12.0})

        first = client.post(
            "/api/v1/commands", json=envelope, headers={CSRF_HEADER_NAME: csrf}
        )
        second = client.post(
            "/api/v1/commands", json=envelope, headers={CSRF_HEADER_NAME: csrf}
        )

    assert first.status_code == 200
    assert first.json()["status"] == "applied"
    assert first.json()["result"]["clock"]["speed"] == 12.0
    assert second.json() == first.json()


def test_command_endpoint_rejects_epoch_mismatch_with_receipt(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        csrf = login(client)
        world = client.get("/api/v1/world").json()
        envelope = command(world, "clock.pause", {})
        envelope["request_epoch"] = 999

        response = client.post(
            "/api/v1/commands", json=envelope, headers={CSRF_HEADER_NAME: csrf}
        )

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"
    assert response.json()["reason"] == "request epoch expired"


def test_command_endpoint_rejects_invalid_envelope_without_receipt(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        csrf = login(client)

        response = client.post(
            "/api/v1/commands",
            json={"schema_version": 1, "extra": True},
            headers={CSRF_HEADER_NAME: csrf},
        )

    assert response.status_code == 400


def test_stream_requires_authentication(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        try:
            with client.websocket_connect("/api/v1/stream"):
                raise AssertionError("unauthenticated websocket should not connect")
        except WebSocketDisconnect as exc:
            assert exc.code == 1008


def test_stream_rejects_cross_origin_upgrade(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        login(client)
        try:
            with client.websocket_connect(
                "/api/v1/stream", headers={"Origin": "http://attacker.invalid"}
            ):
                raise AssertionError("cross-origin websocket should not connect")
        except WebSocketDisconnect as exc:
            assert exc.code == 1008


def test_stream_sends_snapshot_and_pong(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        login(client)
        world = client.get("/api/v1/world").json()
        with client.websocket_connect("/api/v1/stream") as websocket:
            snapshot = websocket.receive_json()
            websocket.send_text('{"kind":"ping"}')
            pong = websocket.receive_json()

    assert snapshot["schema_version"] == 1
    assert snapshot["world_id"] == world["world_id"]
    assert snapshot["timeline_id"] == world["timeline_id"]
    assert snapshot["kind"] == "snapshot"
    assert snapshot["payload"]["request_epoch"] == world["request_epoch"]
    assert snapshot["payload"]["clock"]["speed"] == 48.0
    assert pong["kind"] == "pong"


def test_stream_rejects_oversized_client_message(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        login(client)
        with client.websocket_connect("/api/v1/stream") as websocket:
            websocket.receive_json()
            websocket.send_text("x" * 4097)
            try:
                websocket.receive_json()
                raise AssertionError("oversized websocket message should close")
            except WebSocketDisconnect as exc:
                assert exc.code == 1009
