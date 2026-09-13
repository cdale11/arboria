import pytest

from arboria.biology.water import advance_zone_water, apply_watering


def test_zone_water_conserves_and_bounds_flows() -> None:
    result = advance_zone_water(
        zone_water_kg=0.12,
        capacity_kg=0.20,
        root_water_kg=0.05,
        leaf_area_m2=0.06,
        dt_seconds=300.0,
    )

    assert 0.0 <= result.zone_water_kg <= 0.20
    assert result.root_uptake_kg <= 0.12
    assert result.transpiration_kg <= 0.05 + result.root_uptake_kg
    assert 0.0 <= result.water_stress_factor <= 1.0


def test_zone_water_drains_above_capacity_accounting() -> None:
    zone_after, reservoir_after, drainage = apply_watering(
        zone_water_kg=0.19,
        capacity_kg=0.20,
        reservoir_kg=1.0,
        water_kg=0.05,
    )

    assert zone_after == pytest.approx(0.20)
    assert reservoir_after == pytest.approx(0.95)
    assert drainage == pytest.approx(0.04)


def test_watering_rejects_over_reservoir_or_invalid() -> None:
    with pytest.raises(ValueError, match="not enough reservoir"):
        apply_watering(
            zone_water_kg=0.1, capacity_kg=0.2, reservoir_kg=0.01, water_kg=0.02
        )
    with pytest.raises(ValueError, match="cannot be negative"):
        advance_zone_water(
            zone_water_kg=-0.1,
            capacity_kg=0.2,
            root_water_kg=0.05,
            leaf_area_m2=0.06,
            dt_seconds=300.0,
        )
