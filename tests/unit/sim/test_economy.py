"""Unit tests for the pure R1 shop economy kernel."""

from __future__ import annotations

import pytest

from arboria.sim.economy import (
    PRICE_TABLE,
    STARTING_CASH_MINOR,
    EconomyState,
    apply_buy_plant,
    apply_buy_water,
    apply_sell_plant,
    buy_water_cost_minor,
    economy_from_payload,
    economy_to_payload,
    starter_economy,
)


def test_starter_economy_has_cash_and_full_demand() -> None:
    state = starter_economy()

    assert state.cash_minor == STARTING_CASH_MINOR
    assert set(state.demand_remaining) == set(PRICE_TABLE)
    assert all(remaining > 0 for remaining in state.demand_remaining.values())


def test_buy_water_charges_cash_and_fills_reservoir() -> None:
    state = starter_economy()

    next_state, reservoir_after, cost = apply_buy_water(state, 2.0, 0.5)

    assert cost == 100
    assert reservoir_after == pytest.approx(2.5)
    assert next_state.cash_minor == STARTING_CASH_MINOR - 100


def test_buy_water_rejects_bad_requests() -> None:
    state = starter_economy()
    with pytest.raises(ValueError, match="must be positive"):
        apply_buy_water(state, 2.0, 0.0)
    with pytest.raises(ValueError, match="capacity exceeded"):
        apply_buy_water(state, 4.9, 0.5)
    poor = EconomyState(cash_minor=0, demand_remaining=dict(state.demand_remaining))
    with pytest.raises(ValueError, match="insufficient cash"):
        apply_buy_water(poor, 2.0, 0.5)
    with pytest.raises(ValueError, match="water_kg must be finite"):
        buy_water_cost_minor(float("inf"))


def test_buy_and_sell_plant_move_cash_and_demand() -> None:
    state = starter_economy()
    prices = PRICE_TABLE["ocimum_basilicum"]

    after_buy, cost = apply_buy_plant(state, "ocimum_basilicum")
    assert cost == prices.buy_minor
    assert after_buy.cash_minor == STARTING_CASH_MINOR - prices.buy_minor

    after_sell, credit = apply_sell_plant(after_buy, "ocimum_basilicum")
    assert credit == prices.sell_minor
    assert after_sell.cash_minor == STARTING_CASH_MINOR - prices.buy_minor + prices.sell_minor
    assert after_sell.demand_remaining["ocimum_basilicum"] == prices.demand - 1


def test_buy_then_sell_always_loses_cash() -> None:
    for species_id in PRICE_TABLE:
        state = starter_economy()
        after_buy, _ = apply_buy_plant(state, species_id)
        after_sell, _ = apply_sell_plant(after_buy, species_id)
        assert after_sell.cash_minor < STARTING_CASH_MINOR


def test_sales_stop_when_demand_runs_out() -> None:
    state = starter_economy()
    prices = PRICE_TABLE["crassula_ovata"]
    for _ in range(prices.demand):
        state, _ = apply_sell_plant(state, "crassula_ovata")
    assert state.demand_remaining["crassula_ovata"] == 0
    with pytest.raises(ValueError, match="no buyer demand"):
        apply_sell_plant(state, "crassula_ovata")


def test_unknown_species_and_bad_cash_are_rejected() -> None:
    state = starter_economy()
    with pytest.raises(ValueError, match="unknown species"):
        apply_buy_plant(state, "arabidopsis_thaliana")
    with pytest.raises(ValueError, match="unknown species"):
        apply_sell_plant(state, "arabidopsis_thaliana")
    with pytest.raises(ValueError, match="insufficient cash"):
        apply_buy_plant(
            EconomyState(cash_minor=0, demand_remaining=dict(state.demand_remaining)),
            "juniperus_procumbens",
        )
    with pytest.raises(ValueError, match="cannot be negative"):
        apply_buy_plant(
            EconomyState(cash_minor=-1, demand_remaining=dict(state.demand_remaining)),
            "ocimum_basilicum",
        )


def test_economy_payload_round_trip_and_fallback() -> None:
    state = starter_economy()
    state, _ = apply_sell_plant(state, "quercus_robur")

    restored = economy_from_payload(economy_to_payload(state))

    assert restored == state
    assert economy_from_payload({}) == starter_economy()
    assert economy_from_payload(None) == starter_economy()
    with pytest.raises(ValueError, match="invalid economy payload"):
        economy_from_payload({"cash_minor": 1.5, "demand_remaining": []})
