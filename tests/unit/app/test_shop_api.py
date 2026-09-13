from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from arboria.app.auth import CSRF_COOKIE_NAME, CSRF_HEADER_NAME, configure_password
from arboria.app.server import create_app
from arboria.sim.economy import PRICE_TABLE, STARTING_CASH_MINOR


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


def command(world: Any, kind: str, payload: dict[str, object]) -> Any:
    return {
        "schema_version": 1,
        "command_id": str(uuid4()),
        "world_id": world["world_id"],
        "timeline_id": world["timeline_id"],
        "request_epoch": world["request_epoch"],
        "kind": kind,
        "payload": payload,
    }


def submit(client: TestClient, csrf: str, kind: str, payload: dict[str, object]) -> Any:
    world = client.get("/api/v1/world").json()
    response = client.post(
        "/api/v1/commands",
        json=command(world, kind, payload),
        headers={CSRF_HEADER_NAME: csrf},
    )
    assert response.status_code == 200
    return response.json()


def test_shop_reports_cash_and_demand(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        login(client)
        payload = client.get("/api/v1/plants").json()

    assert payload["nursery"]["cash_minor"] == STARTING_CASH_MINOR
    assert len(payload["nursery"]["demand_remaining"]) == len(PRICE_TABLE)


def test_buy_water_command_fills_reservoir_for_cash(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        csrf = login(client)
        before = client.get("/api/v1/plants").json()
        receipt = submit(client, csrf, "shop.buy_water", {"water_kg": 0.5})
        after = client.get("/api/v1/plants").json()

    assert receipt["status"] == "applied"
    assert receipt["result"]["cost_minor"] == 100
    assert after["nursery"]["reservoir_kg"] == before["nursery"]["reservoir_kg"] + 0.5
    assert after["nursery"]["cash_minor"] == before["nursery"]["cash_minor"] - 100


def test_buy_water_rejects_over_capacity_and_low_cash(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        csrf = login(client)
        full = submit(client, csrf, "shop.buy_water", {"water_kg": 3.1})
        for _ in range(5):
            bought = submit(
                client, csrf, "shop.buy_plant", {"species_id": "juniperus_procumbens"}
            )
            assert bought["status"] == "applied"
        poor = submit(client, csrf, "shop.buy_water", {"water_kg": 20.0})
        after = client.get("/api/v1/plants").json()

    assert full["status"] == "rejected"
    assert poor["status"] == "rejected"
    assert "insufficient cash" in (poor["reason"] or "")
    assert after["nursery"]["cash_minor"] == STARTING_CASH_MINOR - 5 * 3500


def test_buy_plant_adds_live_plant(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        csrf = login(client)
        receipt = submit(client, csrf, "shop.buy_plant", {"species_id": "crassula_ovata"})
        payload = client.get("/api/v1/plants").json()

    assert receipt["status"] == "applied"
    assert receipt["result"]["plant_id"] == 3
    assert receipt["result"]["cost_minor"] == 1200
    assert len(payload["plants"]) == 3
    bought = payload["plants"][2]
    assert bought["species_id"] == "crassula_ovata"
    assert bought["alive"] is True
    assert payload["nursery"]["cash_minor"] == STARTING_CASH_MINOR - 1200


def test_sell_plant_credits_cash_and_consumes_demand(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        csrf = login(client)
        bought = submit(
            client, csrf, "shop.buy_plant", {"species_id": "crassula_ovata"}
        )
        plant_id = int(bought["result"]["plant_id"])
        sold = submit(client, csrf, "shop.sell_plant", {"plant_id": plant_id})
        payload = client.get("/api/v1/plants").json()

    assert sold["status"] == "applied"
    assert sold["result"]["credit_minor"] == 400
    assert [plant["plant_id"] for plant in payload["plants"]] == [1, 2]
    assert payload["nursery"]["cash_minor"] == STARTING_CASH_MINOR - 1200 + 400
    demand = {
        entry["species_id"]: entry["remaining"]
        for entry in payload["nursery"]["demand_remaining"]
    }
    assert demand["crassula_ovata"] == 1


def test_protected_plant_cannot_be_sold_until_unprotected(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        csrf = login(client)
        protected = submit(client, csrf, "nursery.protect", {"plant_id": 1})
        blocked = submit(client, csrf, "shop.sell_plant", {"plant_id": 1})
        listed = client.get("/api/v1/plants").json()
        detail = client.get("/api/v1/plants/1").json()
        unprotected = submit(client, csrf, "nursery.unprotect", {"plant_id": 1})
        sold = submit(client, csrf, "shop.sell_plant", {"plant_id": 1})

    assert protected["status"] == "applied"
    assert blocked["status"] == "rejected"
    assert "protected" in (blocked["reason"] or "")
    assert listed["nursery"]["protected_plant_ids"] == [1]
    assert listed["plants"][0]["protected"] is True
    assert detail["protected"] is True
    assert unprotected["status"] == "applied"
    assert sold["status"] == "applied"


def test_repeated_sell_of_same_plant_is_rejected(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        csrf = login(client)
        bought = submit(
            client, csrf, "shop.buy_plant", {"species_id": "crassula_ovata"}
        )
        plant_id = int(bought["result"]["plant_id"])
        first = submit(client, csrf, "shop.sell_plant", {"plant_id": plant_id})
        second = submit(client, csrf, "shop.sell_plant", {"plant_id": plant_id})
        payload = client.get("/api/v1/plants").json()

    assert first["status"] == "applied"
    assert second["status"] == "rejected"
    assert payload["nursery"]["cash_minor"] == STARTING_CASH_MINOR - 1200 + 400


def test_demand_exhaustion_blocks_further_sales(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        csrf = login(client)
        for _ in range(3):
            bought = submit(
                client, csrf, "shop.buy_plant", {"species_id": "ocimum_basilicum"}
            )
            assert bought["status"] == "applied"
            sold = submit(
                client, csrf, "shop.sell_plant", {"plant_id": int(bought["result"]["plant_id"])}
            )
            assert sold["status"] == "applied"
        bought = submit(
            client, csrf, "shop.buy_plant", {"species_id": "ocimum_basilicum"}
        )
        exhausted = submit(
            client, csrf, "shop.sell_plant", {"plant_id": int(bought["result"]["plant_id"])}
        )
        payload = client.get("/api/v1/plants").json()

    assert exhausted["status"] == "rejected"
    demand = {
        entry["species_id"]: entry["remaining"]
        for entry in payload["nursery"]["demand_remaining"]
    }
    assert demand["ocimum_basilicum"] == 0


def test_duplicate_command_id_applies_buy_water_once(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        csrf = login(client)
        world = client.get("/api/v1/world").json()
        envelope = command(world, "shop.buy_water", {"water_kg": 0.5})
        envelope["command_id"] = "00000000-0000-0000-0000-000000000001"
        first = client.post(
            "/api/v1/commands", json=envelope, headers={CSRF_HEADER_NAME: csrf}
        ).json()
        second = client.post(
            "/api/v1/commands", json=envelope, headers={CSRF_HEADER_NAME: csrf}
        ).json()
        payload = client.get("/api/v1/plants").json()

    assert first["status"] == "applied"
    assert second["status"] == "applied"
    assert second["result"]["cost_minor"] == 100
    assert payload["nursery"]["cash_minor"] == STARTING_CASH_MINOR - 100
    assert payload["nursery"]["reservoir_kg"] == 2.5


def test_buy_then_sell_loses_cash(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        csrf = login(client)
        bought = submit(client, csrf, "shop.buy_plant", {"species_id": "ficus_benjamina"})
        submit(
            client, csrf, "shop.sell_plant", {"plant_id": int(bought["result"]["plant_id"])}
        )
        payload = client.get("/api/v1/plants").json()

    assert payload["nursery"]["cash_minor"] == STARTING_CASH_MINOR - 2500 + 800


def test_checkpoint_restore_preserves_shop_state(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    configure_auth(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        csrf = login(client)
        submit(client, csrf, "shop.buy_water", {"water_kg": 0.5})
        submit(client, csrf, "shop.buy_plant", {"species_id": "crassula_ovata"})
        before = client.get("/api/v1/plants").json()
        saved = client.post(
            "/api/v1/saves/named",
            json={"name": "shop"},
            headers={CSRF_HEADER_NAME: csrf},
        )
        assert saved.status_code == 200
        sold = submit(client, csrf, "shop.sell_plant", {"plant_id": 3})
        assert sold["status"] == "applied"
        restored = client.post(
            "/api/v1/saves/restore",
            json={"name": "shop"},
            headers={CSRF_HEADER_NAME: csrf},
        )
        after = client.get("/api/v1/plants").json()

    assert restored.status_code == 200
    assert after["nursery"]["cash_minor"] == before["nursery"]["cash_minor"]
    assert [plant["plant_id"] for plant in after["plants"]] == [1, 2, 3]
    assert after["plants"][2]["species_id"] == "crassula_ovata"
    assert after["nursery"]["demand_remaining"] == before["nursery"]["demand_remaining"]
