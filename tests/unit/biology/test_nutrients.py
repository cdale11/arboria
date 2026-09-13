"""Unit tests for the pure N/P/K uptake, stress, damage, and death kernel."""

from __future__ import annotations

import pytest

from arboria.biology.nutrients import (
    NutrientParameters,
    NutrientZone,
    advance_plant_nutrients,
    advance_stress_damage,
    nutrient_stress_factor,
)

PARAMETERS = NutrientParameters(
    uptake_rate_per_s=1.0e-4,
    reference_nitrogen_kg=0.001,
    reference_phosphorus_kg=0.0002,
    reference_potassium_kg=0.0004,
    capacity_nitrogen_kg=0.002,
    capacity_phosphorus_kg=0.0004,
    capacity_potassium_kg=0.0008,
    damage_stress_threshold=0.5,
    damage_rate_per_s=1.0e-6,
)

ZONE = NutrientZone(nitrogen_kg=0.02, phosphorus_kg=0.004, potassium_kg=0.008)


def test_uptake_moves_zone_nutrients_into_root_pools() -> None:
    result = advance_plant_nutrients(
        zone=ZONE,
        root_nitrogen_kg=0.001,
        root_phosphorus_kg=0.0002,
        root_potassium_kg=0.0004,
        dt_seconds=300.0,
        parameters=PARAMETERS,
    )

    assert result.uptake_nitrogen_kg > 0.0
    assert result.uptake_phosphorus_kg > 0.0
    assert result.uptake_potassium_kg > 0.0
    assert result.zone.nitrogen_kg == pytest.approx(0.02 - result.uptake_nitrogen_kg)
    assert result.root_nitrogen_kg == pytest.approx(0.001 + result.uptake_nitrogen_kg)
    assert result.nutrient_stress_factor == pytest.approx(1.0)


def test_uptake_is_bounded_by_zone_supply_and_pool_capacity() -> None:
    empty = NutrientZone(nitrogen_kg=0.0, phosphorus_kg=0.0, potassium_kg=0.0)
    result = advance_plant_nutrients(
        zone=empty,
        root_nitrogen_kg=0.001,
        root_phosphorus_kg=0.0002,
        root_potassium_kg=0.0004,
        dt_seconds=300.0,
        parameters=PARAMETERS,
    )
    assert result.uptake_nitrogen_kg == 0.0
    assert result.zone.nitrogen_kg == 0.0

    full = advance_plant_nutrients(
        zone=ZONE,
        root_nitrogen_kg=0.002,
        root_phosphorus_kg=0.0004,
        root_potassium_kg=0.0008,
        dt_seconds=300.0,
        parameters=PARAMETERS,
    )
    assert full.uptake_nitrogen_kg == 0.0
    assert full.root_nitrogen_kg == pytest.approx(0.002)


def test_stress_factor_uses_limiting_nutrient() -> None:
    assert (
        nutrient_stress_factor(
            root_nitrogen_kg=0.001,
            root_phosphorus_kg=0.0001,
            root_potassium_kg=0.0004,
            parameters=PARAMETERS,
        )
        == pytest.approx(0.5)
    )
    assert (
        nutrient_stress_factor(
            root_nitrogen_kg=0.0,
            root_phosphorus_kg=0.0,
            root_potassium_kg=0.0,
            parameters=PARAMETERS,
        )
        == 0.0
    )
    assert (
        nutrient_stress_factor(
            root_nitrogen_kg=0.010,
            root_phosphorus_kg=0.010,
            root_potassium_kg=0.010,
            parameters=PARAMETERS,
        )
        == 1.0
    )


def test_damage_accrues_below_threshold_and_kills_at_one() -> None:
    mild = advance_stress_damage(
        damage_fraction=0.0,
        alive=True,
        combined_stress_factor=0.5,
        dt_seconds=300.0,
        parameters=PARAMETERS,
    )
    assert mild.damage_fraction == 0.0
    assert mild.alive is True

    stressed = advance_stress_damage(
        damage_fraction=0.0,
        alive=True,
        combined_stress_factor=0.0,
        dt_seconds=300.0,
        parameters=PARAMETERS,
    )
    assert stressed.damage_fraction == pytest.approx(1.0e-6 * 300.0)
    assert stressed.alive is True

    dying = advance_stress_damage(
        damage_fraction=0.9999,
        alive=True,
        combined_stress_factor=0.0,
        dt_seconds=300.0,
        parameters=PARAMETERS,
    )
    assert dying.damage_fraction == 1.0
    assert dying.alive is False


def test_damage_is_irreversible_but_halts_when_stress_relents() -> None:
    damaged = advance_stress_damage(
        damage_fraction=0.25,
        alive=True,
        combined_stress_factor=1.0,
        dt_seconds=300.0,
        parameters=PARAMETERS,
    )
    assert damaged.damage_fraction == 0.25
    assert damaged.alive is True

    dead = advance_stress_damage(
        damage_fraction=1.0,
        alive=False,
        combined_stress_factor=1.0,
        dt_seconds=300.0,
        parameters=PARAMETERS,
    )
    assert dead.alive is False


def test_kernel_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="cannot be negative"):
        advance_plant_nutrients(
            zone=NutrientZone(nitrogen_kg=-1.0, phosphorus_kg=0.0, potassium_kg=0.0),
            root_nitrogen_kg=0.001,
            root_phosphorus_kg=0.0002,
            root_potassium_kg=0.0004,
            dt_seconds=300.0,
            parameters=PARAMETERS,
        )
    with pytest.raises(ValueError, match="dt_seconds"):
        advance_plant_nutrients(
            zone=ZONE,
            root_nitrogen_kg=0.001,
            root_phosphorus_kg=0.0002,
            root_potassium_kg=0.0004,
            dt_seconds=0.0,
            parameters=PARAMETERS,
        )
    bad_capacity = NutrientParameters(
        uptake_rate_per_s=1.0e-4,
        reference_nitrogen_kg=0.001,
        reference_phosphorus_kg=0.0002,
        reference_potassium_kg=0.0004,
        capacity_nitrogen_kg=0.0005,
        capacity_phosphorus_kg=0.0004,
        capacity_potassium_kg=0.0008,
        damage_stress_threshold=0.5,
        damage_rate_per_s=1.0e-6,
    )
    with pytest.raises(ValueError, match="cannot be below"):
        nutrient_stress_factor(
            root_nitrogen_kg=0.001,
            root_phosphorus_kg=0.0002,
            root_potassium_kg=0.0004,
            parameters=bad_capacity,
        )
