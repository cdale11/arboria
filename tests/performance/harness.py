"""Reproducible headless nursery scale/soak harness for R1 performance evidence.

This module builds large pure-Python nurseries through the public
`add_starter_plant`/`advance_nursery` kernels (no server, network, DB, or
rendering), times whole-biology ticks, and checks stability invariants. It is
imported by the `performance`-marked pytest suite under `tests/performance`
and is intentionally separate from the unit suite.

The simulation kernels are pure Python and not yet vectorized. This harness
records honest wall-clock numbers and bottleneck notes rather than asserting
that every provisional gate from `docs/testing.md` already passes.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass

from arboria.biology.nutrients import NutrientZone
from arboria.biology.organs import Organ
from arboria.sim.nursery import (
    add_starter_plant,
    advance_nursery,
    starter_nutrient_zones,
    starter_organs,
    starter_species_by_plant,
    starter_zones,
    summarize,
)

# Round-robin species so heterogeneous mature canopies are represented, not
# thousands of identical seedlings (docs/testing.md section 7).
SCALE_SPECIES = (
    "ocimum_basilicum",
    "quercus_robur",
    "ficus_benjamina",
    "crassula_ovata",
    "juniperus_procumbens",
    "solanum_lycopersicum",
)

# One simulated year: 365 days * 86400 s/day / 300 s per tick.
TICKS_PER_YEAR = 365 * 86400 // 300


@dataclass(frozen=True)
class NurseryState:
    organs: list[Organ]
    zones: dict[int, float]
    nutrient_zones: dict[int, NutrientZone]
    species_by_plant: dict[int, str]


@dataclass(frozen=True)
class TimingResult:
    plants: int
    samples: int
    p50_ms: float
    p95_ms: float
    p99_ms: float
    max_ms: float


def build_nursery(plants: int) -> NurseryState:
    """Construct a heterogeneous `plants`-count nursery with starter geometry."""
    organs = starter_organs()
    zones = starter_zones()
    nutrient_zones = starter_nutrient_zones()
    mapping = starter_species_by_plant()
    index = 0
    while len({organ.plant_id for organ in organs}) < plants:
        species_id = SCALE_SPECIES[index % len(SCALE_SPECIES)]
        organs, zones, nutrient_zones, mapping, _ = add_starter_plant(
            organs, zones, nutrient_zones, mapping, species_id
        )
        index += 1
    return NurseryState(organs, zones, nutrient_zones, mapping)


def _percentile(values: list[float], fraction: float) -> float:
    if not values:
        raise ValueError("cannot compute a percentile from no samples")
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(math.ceil(fraction * len(ordered))) - 1))
    return ordered[index]


def measure_tick(state: NurseryState, samples: int = 30) -> TimingResult:
    """Time `samples` successive single-tick advancements and return percentiles."""
    organs = state.organs
    zones = state.zones
    nutrient_zones = state.nutrient_zones
    durations: list[float] = []
    for _ in range(samples):
        start = time.perf_counter()
        result = advance_nursery(organs, zones, nutrient_zones, 1, state.species_by_plant)
        durations.append(time.perf_counter() - start)
        organs, zones, nutrient_zones = (
            result.organs,
            result.zones,
            result.nutrient_zones,
        )
    return TimingResult(
        plants=len({organ.plant_id for organ in state.organs}),
        samples=samples,
        p50_ms=_percentile(durations, 0.50) * 1000.0,
        p95_ms=_percentile(durations, 0.95) * 1000.0,
        p99_ms=_percentile(durations, 0.99) * 1000.0,
        max_ms=max(durations) * 1000.0,
    )


@dataclass(frozen=True)
class SoakCheckpoint:
    plants: int
    organ_count: int
    dead_plant_count: int
    reserve_carbon_kg: float
    structural_carbon_kg: float
    zone_water_kg: float
    finite: bool
    within_capacity: bool


def run_soak(state: NurseryState, ticks: int) -> SoakCheckpoint:
    """Advance `ticks` in chunked batches, checking invariants at the end."""
    organs = state.organs
    zones = state.zones
    nutrient_zones = state.nutrient_zones
    remaining = ticks
    chunk = 48  # one sim day per advance call, bounding peak per-call work
    while remaining > 0:
        step = min(chunk, remaining)
        result = advance_nursery(organs, zones, nutrient_zones, step, state.species_by_plant)
        organs, zones, nutrient_zones = (
            result.organs,
            result.zones,
            result.nutrient_zones,
        )
        remaining -= step
    summary = summarize(organs, zones, nutrient_zones, species_by_plant=state.species_by_plant)
    finite = all(
        math.isfinite(value)
        for value in (
            summary.reserve_carbon_kg,
            summary.structural_carbon_kg,
            summary.zone_water_kg,
        )
    )
    within_capacity = all(0.0 <= water_kg <= 0.2 + 1e-9 for water_kg in zones.values())
    return SoakCheckpoint(
        plants=summary.plant_count,
        organ_count=summary.organ_count,
        dead_plant_count=summary.dead_plant_count,
        reserve_carbon_kg=summary.reserve_carbon_kg,
        structural_carbon_kg=summary.structural_carbon_kg,
        zone_water_kg=summary.zone_water_kg,
        finite=finite,
        within_capacity=within_capacity,
    )
