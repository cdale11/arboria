"""Bounded root-zone water kernel for R1 nursery care."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class ZoneWaterState:
    zone_water_kg: float
    capacity_kg: float


@dataclass(frozen=True)
class ZoneWaterResult:
    zone_water_kg: float
    root_uptake_kg: float
    transpiration_kg: float
    drainage_kg: float
    water_stress_factor: float


def advance_zone_water(
    *,
    zone_water_kg: float,
    capacity_kg: float,
    root_water_kg: float,
    leaf_area_m2: float,
    dt_seconds: float,
    conductance_kg_s: float = 2.0e-7,
    transpiration_kg_s_m2: float = 4.0e-7,
) -> ZoneWaterResult:
    """Exchange water between one well-mixed root zone and its plant.

    Uptake moves zone water into the root pool, transpiration releases plant
    water to the atmosphere, and above-capacity zone water drains as a boundary
    flux. All flows are bounded by donor supply over the interval.
    """
    for name, value in {
        "zone_water_kg": zone_water_kg,
        "capacity_kg": capacity_kg,
        "root_water_kg": root_water_kg,
        "leaf_area_m2": leaf_area_m2,
        "dt_seconds": dt_seconds,
        "conductance_kg_s": conductance_kg_s,
        "transpiration_kg_s_m2": transpiration_kg_s_m2,
    }.items():
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
        if value < 0.0:
            raise ValueError(f"{name} cannot be negative")
    if capacity_kg <= 0.0:
        raise ValueError("capacity_kg must be positive")
    # Bounded conductance form: uptake scales with zone fullness and can never
    # exceed available zone water over the interval.
    uptake = min(
        zone_water_kg,
        conductance_kg_s * (0.5 + zone_water_kg / capacity_kg) * dt_seconds,
    )
    available_plant_water = root_water_kg + uptake
    transpiration = min(
        available_plant_water, transpiration_kg_s_m2 * leaf_area_m2 * dt_seconds
    )
    zone_after = zone_water_kg - uptake
    drainage = max(0.0, zone_after - capacity_kg)
    zone_after -= drainage
    stress = max(0.0, min(1.0, 0.35 + 0.65 * (zone_after / capacity_kg)))
    return ZoneWaterResult(
        zone_water_kg=zone_after,
        root_uptake_kg=uptake,
        transpiration_kg=transpiration,
        drainage_kg=drainage,
        water_stress_factor=stress,
    )


def apply_watering(
    *,
    zone_water_kg: float,
    capacity_kg: float,
    reservoir_kg: float,
    water_kg: float,
) -> tuple[float, float, float]:
    """Transfer reservoir water into a root zone; return zone, reservoir, drainage."""
    for name, value in {
        "zone_water_kg": zone_water_kg,
        "capacity_kg": capacity_kg,
        "reservoir_kg": reservoir_kg,
        "water_kg": water_kg,
    }.items():
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
        if value < 0.0:
            raise ValueError(f"{name} cannot be negative")
    if capacity_kg <= 0.0:
        raise ValueError("capacity_kg must be positive")
    if water_kg == 0.0:
        return zone_water_kg, reservoir_kg, 0.0
    if water_kg > reservoir_kg:
        raise ValueError("not enough reservoir water")
    zone_after = zone_water_kg + water_kg
    drainage = max(0.0, zone_after - capacity_kg)
    zone_after -= drainage
    return zone_after, reservoir_kg - water_kg, drainage
