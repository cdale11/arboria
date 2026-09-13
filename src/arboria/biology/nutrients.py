"""Pure N/P/K uptake, deficiency stress, damage, and death kernels for R1.

Scope: well-mixed per-plant substrate N/P/K supply, bounded first-order
root uptake into finite luxury pools, Liebig-minimum deficiency stress, and
irreversible stress-damage accumulation leading to organ death. Fertilizer
inputs, layered substrate, pH/buffering, waterlogging, and damage recovery
are deferred and documented as unsupported in this slice.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class NutrientZone:
    nitrogen_kg: float
    phosphorus_kg: float
    potassium_kg: float


@dataclass(frozen=True)
class NutrientParameters:
    uptake_rate_per_s: float
    reference_nitrogen_kg: float
    reference_phosphorus_kg: float
    reference_potassium_kg: float
    capacity_nitrogen_kg: float
    capacity_phosphorus_kg: float
    capacity_potassium_kg: float
    damage_stress_threshold: float
    damage_rate_per_s: float


@dataclass(frozen=True)
class NutrientUptakeResult:
    zone: NutrientZone
    root_nitrogen_kg: float
    root_phosphorus_kg: float
    root_potassium_kg: float
    uptake_nitrogen_kg: float
    uptake_phosphorus_kg: float
    uptake_potassium_kg: float
    nutrient_stress_factor: float


@dataclass(frozen=True)
class DamageResult:
    damage_fraction: float
    alive: bool


def validate_nutrient_zone(zone: NutrientZone) -> None:
    for name in ("nitrogen_kg", "phosphorus_kg", "potassium_kg"):
        value = getattr(zone, name)
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
        if value < 0.0:
            raise ValueError(f"{name} cannot be negative")


def validate_nutrient_parameters(parameters: NutrientParameters) -> None:
    for name in (
        "uptake_rate_per_s",
        "reference_nitrogen_kg",
        "reference_phosphorus_kg",
        "reference_potassium_kg",
        "capacity_nitrogen_kg",
        "capacity_phosphorus_kg",
        "capacity_potassium_kg",
        "damage_rate_per_s",
    ):
        value = getattr(parameters, name)
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
        if value <= 0.0:
            raise ValueError(f"{name} must be positive")
    threshold = parameters.damage_stress_threshold
    if not math.isfinite(threshold) or threshold <= 0.0 or threshold > 1.0:
        raise ValueError("damage_stress_threshold must be within (0, 1]")
    pairs = (
        ("reference_nitrogen_kg", "capacity_nitrogen_kg"),
        ("reference_phosphorus_kg", "capacity_phosphorus_kg"),
        ("reference_potassium_kg", "capacity_potassium_kg"),
    )
    for reference_name, capacity_name in pairs:
        if getattr(parameters, capacity_name) < getattr(parameters, reference_name):
            raise ValueError(f"{capacity_name} cannot be below {reference_name}")


def nutrient_stress_factor(
    *,
    root_nitrogen_kg: float,
    root_phosphorus_kg: float,
    root_potassium_kg: float,
    parameters: NutrientParameters,
) -> float:
    """Liebig-minimum deficiency factor from root mobile pools, bounded [0,1]."""
    validate_nutrient_parameters(parameters)
    for name, value in {
        "root_nitrogen_kg": root_nitrogen_kg,
        "root_phosphorus_kg": root_phosphorus_kg,
        "root_potassium_kg": root_potassium_kg,
    }.items():
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
        if value < 0.0:
            raise ValueError(f"{name} cannot be negative")
    ratios = (
        root_nitrogen_kg / parameters.reference_nitrogen_kg,
        root_phosphorus_kg / parameters.reference_phosphorus_kg,
        root_potassium_kg / parameters.reference_potassium_kg,
    )
    return max(0.0, min(1.0, min(ratios)))


def advance_plant_nutrients(
    *,
    zone: NutrientZone,
    root_nitrogen_kg: float,
    root_phosphorus_kg: float,
    root_potassium_kg: float,
    dt_seconds: float,
    parameters: NutrientParameters,
) -> NutrientUptakeResult:
    """Move substrate N/P/K into root pools with bounded first-order uptake.

    Each element uptake is bounded by substrate supply and by remaining luxury
    headroom, so neither pools nor zones can go negative and pools cannot
    exceed capacity. Returns the updated zone, root pools, per-element uptake,
    and the post-uptake deficiency stress factor.
    """
    validate_nutrient_zone(zone)
    validate_nutrient_parameters(parameters)
    if not math.isfinite(dt_seconds) or dt_seconds <= 0.0:
        raise ValueError("dt_seconds must be positive and finite")
    for name, value in {
        "root_nitrogen_kg": root_nitrogen_kg,
        "root_phosphorus_kg": root_phosphorus_kg,
        "root_potassium_kg": root_potassium_kg,
    }.items():
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
        if value < 0.0:
            raise ValueError(f"{name} cannot be negative")
    fraction = min(1.0, parameters.uptake_rate_per_s * dt_seconds)
    uptake_n = min(
        zone.nitrogen_kg,
        max(0.0, parameters.capacity_nitrogen_kg - root_nitrogen_kg) * fraction,
    )
    uptake_p = min(
        zone.phosphorus_kg,
        max(0.0, parameters.capacity_phosphorus_kg - root_phosphorus_kg) * fraction,
    )
    uptake_k = min(
        zone.potassium_kg,
        max(0.0, parameters.capacity_potassium_kg - root_potassium_kg) * fraction,
    )
    roots = (
        root_nitrogen_kg + uptake_n,
        root_phosphorus_kg + uptake_p,
        root_potassium_kg + uptake_k,
    )
    updated = NutrientZone(
        nitrogen_kg=zone.nitrogen_kg - uptake_n,
        phosphorus_kg=zone.phosphorus_kg - uptake_p,
        potassium_kg=zone.potassium_kg - uptake_k,
    )
    validate_nutrient_zone(updated)
    return NutrientUptakeResult(
        zone=updated,
        root_nitrogen_kg=roots[0],
        root_phosphorus_kg=roots[1],
        root_potassium_kg=roots[2],
        uptake_nitrogen_kg=uptake_n,
        uptake_phosphorus_kg=uptake_p,
        uptake_potassium_kg=uptake_k,
        nutrient_stress_factor=nutrient_stress_factor(
            root_nitrogen_kg=roots[0],
            root_phosphorus_kg=roots[1],
            root_potassium_kg=roots[2],
            parameters=parameters,
        ),
    )


def advance_stress_damage(
    *,
    damage_fraction: float,
    alive: bool,
    combined_stress_factor: float,
    dt_seconds: float,
    parameters: NutrientParameters,
) -> DamageResult:
    """Accumulate irreversible stress damage; kill the organ at damage 1.0.

    Damage accrues only while the combined stress factor sits below the
    threshold, proportional to the shortfall. R1 has no recovery pathway:
    relieved stress halts further damage but never repairs it.
    """
    validate_nutrient_parameters(parameters)
    if not math.isfinite(damage_fraction) or damage_fraction < 0.0 or damage_fraction > 1.0:
        raise ValueError("damage_fraction must be within [0, 1]")
    if not math.isfinite(combined_stress_factor):
        raise ValueError("combined_stress_factor must be finite")
    if not math.isfinite(dt_seconds) or dt_seconds <= 0.0:
        raise ValueError("dt_seconds must be positive and finite")
    if not alive:
        return DamageResult(damage_fraction=damage_fraction, alive=False)
    threshold = parameters.damage_stress_threshold
    if combined_stress_factor >= threshold:
        return DamageResult(damage_fraction=damage_fraction, alive=True)
    shortfall = (threshold - max(0.0, combined_stress_factor)) / threshold
    damage = min(1.0, damage_fraction + parameters.damage_rate_per_s * shortfall * dt_seconds)
    return DamageResult(damage_fraction=damage, alive=damage < 1.0)
