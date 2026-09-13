"""Pure R1 shop economy: integer cash, finite demand, real plant inventory.

Money is tracked in integer minor units and can never go negative. Plants are
real nursery topology: buying adds starter organs, selling removes them and
consumes finite per-species buyer demand. Sale prices sit below purchase
prices structurally, so buy-then-sell always loses cash. No credit, no
random pricing, no synthetic profit exists in this slice.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

STARTING_CASH_MINOR = 20000
WATER_PRICE_PER_KG_MINOR = 200
RESERVOIR_CAPACITY_KG = 5.0


@dataclass(frozen=True)
class SpeciesPrices:
    buy_minor: int
    sell_minor: int
    demand: int


PRICE_TABLE: dict[str, SpeciesPrices] = {
    "ocimum_basilicum": SpeciesPrices(buy_minor=1500, sell_minor=500, demand=3),
    "solanum_lycopersicum": SpeciesPrices(buy_minor=1800, sell_minor=600, demand=3),
    "ficus_benjamina": SpeciesPrices(buy_minor=2500, sell_minor=800, demand=2),
    "crassula_ovata": SpeciesPrices(buy_minor=1200, sell_minor=400, demand=2),
    "juniperus_procumbens": SpeciesPrices(
        buy_minor=3500, sell_minor=1100, demand=2
    ),
    "quercus_robur": SpeciesPrices(buy_minor=3000, sell_minor=900, demand=2),
}


@dataclass(frozen=True)
class EconomyState:
    cash_minor: int
    demand_remaining: dict[str, int]


def starter_economy() -> EconomyState:
    return EconomyState(
        cash_minor=STARTING_CASH_MINOR,
        demand_remaining={
            species_id: prices.demand for species_id, prices in PRICE_TABLE.items()
        },
    )


def validate_economy(state: EconomyState) -> None:
    if not isinstance(state.cash_minor, int) or isinstance(state.cash_minor, bool):
        raise ValueError("cash_minor must be an integer")
    if state.cash_minor < 0:
        raise ValueError("cash_minor cannot be negative")
    if set(state.demand_remaining) != set(PRICE_TABLE):
        raise ValueError("demand_remaining must cover every priced species exactly once")
    for species_id, remaining in state.demand_remaining.items():
        if not isinstance(remaining, int) or isinstance(remaining, bool):
            raise ValueError(f"demand for {species_id} must be an integer")
        if remaining < 0 or remaining > PRICE_TABLE[species_id].demand:
            raise ValueError(f"demand for {species_id} is out of range")


def quote_species(species_id: str) -> SpeciesPrices:
    try:
        return PRICE_TABLE[species_id]
    except KeyError as exc:
        raise ValueError(f"unknown species: {species_id}") from exc


def buy_water_cost_minor(water_kg: float) -> int:
    if not isinstance(water_kg, float | int) or not math.isfinite(float(water_kg)):
        raise ValueError("water_kg must be finite")
    water_kg = float(water_kg)
    if water_kg <= 0.0:
        raise ValueError("water_kg must be positive")
    return max(1, int(math.ceil(water_kg * WATER_PRICE_PER_KG_MINOR)))


def apply_buy_water(
    state: EconomyState, reservoir_kg: float, water_kg: float
) -> tuple[EconomyState, float, int]:
    """Charge cash and add reservoir water; return state, reservoir, cost."""
    validate_economy(state)
    if not math.isfinite(reservoir_kg) or reservoir_kg < 0.0:
        raise ValueError("reservoir_kg must be finite and nonnegative")
    cost = buy_water_cost_minor(water_kg)
    if cost > state.cash_minor:
        raise ValueError("insufficient cash")
    reservoir_after = reservoir_kg + float(water_kg)
    if reservoir_after > RESERVOIR_CAPACITY_KG:
        raise ValueError("reservoir capacity exceeded")
    return (
        EconomyState(
            cash_minor=state.cash_minor - cost,
            demand_remaining=dict(state.demand_remaining),
        ),
        reservoir_after,
        cost,
    )


def apply_buy_plant(state: EconomyState, species_id: str) -> tuple[EconomyState, int]:
    """Charge the purchase price; return the new state and cost."""
    validate_economy(state)
    prices = quote_species(species_id)
    if prices.buy_minor > state.cash_minor:
        raise ValueError("insufficient cash")
    return (
        EconomyState(
            cash_minor=state.cash_minor - prices.buy_minor,
            demand_remaining=dict(state.demand_remaining),
        ),
        prices.buy_minor,
    )


def apply_sell_plant(state: EconomyState, species_id: str) -> tuple[EconomyState, int]:
    """Credit the sale price and consume one unit of demand."""
    validate_economy(state)
    prices = quote_species(species_id)
    remaining = state.demand_remaining[species_id]
    if remaining <= 0:
        raise ValueError("no buyer demand remains for this species")
    demand = dict(state.demand_remaining)
    demand[species_id] = remaining - 1
    return (
        EconomyState(cash_minor=state.cash_minor + prices.sell_minor, demand_remaining=demand),
        prices.sell_minor,
    )


def economy_to_payload(state: EconomyState) -> dict[str, object]:
    validate_economy(state)
    return {
        "cash_minor": state.cash_minor,
        "demand_remaining": [
            {"species_id": species_id, "remaining": state.demand_remaining[species_id]}
            for species_id in sorted(state.demand_remaining)
        ],
    }


def economy_from_payload(payload: object) -> EconomyState:
    if not isinstance(payload, dict) or not payload:
        return starter_economy()
    try:
        cash_minor = payload["cash_minor"]
        entries = payload["demand_remaining"]
        if not isinstance(cash_minor, int) or isinstance(cash_minor, bool):
            raise ValueError("cash_minor must be an integer")
        if not isinstance(entries, list) or not entries:
            raise ValueError("demand_remaining must be a nonempty list")
        demand: dict[str, int] = {}
        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError("demand entries must be objects")
            species_id = entry["species_id"]
            remaining = entry["remaining"]
            if species_id in demand:
                raise ValueError("demand species IDs cannot repeat")
            if not isinstance(species_id, str) or not isinstance(remaining, int):
                raise ValueError("demand entries must carry species_id and integer remaining")
            demand[species_id] = remaining
        state = EconomyState(cash_minor=cash_minor, demand_remaining=demand)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"invalid economy payload: {exc}") from exc
    validate_economy(state)
    return state
