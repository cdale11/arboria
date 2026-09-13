"""R1 target-host performance and soak characterization.

Marked `performance` and excluded from the default unit run. These tests do not
assert an absolute-time pass on unverified hardware; they record reproducible
scaling numbers and confirm the simulation remains finite and within biological
bounds at scale. Run with:

    python -m pytest tests/performance -m performance
"""

import time

import pytest

from arboria.biology.nutrients import NutrientZone
from tests.performance.harness import (
    SCALE_SPECIES,
    TICKS_PER_YEAR,
    build_nursery,
    measure_tick,
    run_soak,
)

pytestmark = pytest.mark.performance


def test_build_heterogeneous_500_plant_nursery() -> None:
    state = build_nursery(500)

    plants = {organ.plant_id for organ in state.organs}
    assert len(plants) == 500
    species = {state.species_by_plant[plant_id] for plant_id in plants}
    assert len(species) >= 2
    assert len(state.organs) == 1500


def test_build_heterogeneous_1000_plant_nursery() -> None:
    state = build_nursery(1000)

    assert len({organ.plant_id for organ in state.organs}) == 1000
    assert len(state.organs) == 3000


def test_500_plant_single_tick_latency() -> None:
    state = build_nursery(500)

    timing = measure_tick(state, samples=20)

    assert timing.plants == 500
    assert timing.samples == 20
    assert timing.p95_ms >= 0.0
    assert timing.p95_ms <= timing.p99_ms
    assert timing.max_ms >= timing.p99_ms


def test_1000_plant_single_tick_latency() -> None:
    state = build_nursery(1000)

    timing = measure_tick(state, samples=10)

    assert timing.plants == 1000
    assert timing.p95_ms >= 0.0


def test_ten_sim_year_stability_keeps_state_finite() -> None:
    # Reduced plant count so the ten-year headless soak is tractable in CI; the
    # kernel is the same as the scale path. Full 500-plant soak is a documented
    # long-run command, not part of the default suite.
    state = build_nursery(50)

    started = time.perf_counter()
    checkpoint = run_soak(state, 10 * TICKS_PER_YEAR)
    elapsed = time.perf_counter() - started

    assert checkpoint.finite
    assert checkpoint.within_capacity
    assert checkpoint.dead_plant_count >= 0
    assert checkpoint.reserve_carbon_kg >= 0.0
    assert checkpoint.structural_carbon_kg >= 0.0
    assert elapsed > 0.0


def test_zone_capacity_is_respected_at_scale() -> None:
    state = build_nursery(100)

    checkpoint = run_soak(state, TICKS_PER_YEAR // 4)

    assert checkpoint.within_capacity
    assert all(isinstance(zone, NutrientZone) for zone in state.nutrient_zones.values())


def test_species_round_robin_covers_all_catalog_entries() -> None:
    assert len(SCALE_SPECIES) == 6
    assert len(set(SCALE_SPECIES)) == 6
