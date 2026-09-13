"""Pure R1 nursery state: starter plants and deterministic per-tick biology."""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

from arboria.biology.carbon import AssimilationParameters, assimilate_carbon
from arboria.biology.growth import GrowthDemand, apply_vegetative_growth
from arboria.biology.organs import (
    Organ,
    OrganKind,
    ResourcePools,
    total_resource_pools,
    validate_topology,
)
from arboria.biology.water import advance_zone_water, apply_watering

# Provisional R1 forcing/parameters. Water/nutrient factors are fixed at 1.0 and
# documented as uncalibrated placeholders, not measured species constants.
BASE_TICK_SECONDS = 300.0
PAR_W_M2 = 250.0
ASSIMILATION_PARAMETERS = AssimilationParameters(
    amax_kg_c_m2_s=1.0e-6,
    half_saturation_w_m2=120.0,
    temperature_factor=1.0,
    water_factor=1.0,
    nutrient_factor=1.0,
)
NURSERY_SCHEMA_VERSION = 2
# Fixed per-tick structural demand factors. Small enough to keep starter pools
# positive for many ticks while remaining visible in inspection totals.
GROWTH_RESERVE_FRACTION = 0.0005
GROWTH_LENGTH_M_PER_TICK = 0.0005
GROWTH_WATER_FRACTION = 0.01
GROWTH_NUTRIENT_FRACTION = 0.005
# Well-mixed R1 root zone per plant. Watering transfers finite reservoir water
# into a zone; above-capacity water drains as an explicit boundary flux.
ZONE_CAPACITY_KG = 0.20
STARTER_ZONE_WATER_KG = 0.12
STARTER_RESERVOIR_KG = 2.0
MAX_WATER_PER_COMMAND_KG = 0.05


@dataclass(frozen=True)
class PlantProjection:
    plant_id: int
    organ_count: int
    leaf_area_m2: float
    stem_length_m: float
    reserve_carbon_kg: float
    structural_carbon_kg: float
    zone_water_kg: float
    water_stress_factor: float


@dataclass(frozen=True)
class NurserySummary:
    plant_count: int
    organ_count: int
    reserve_carbon_kg: float
    structural_carbon_kg: float
    atmospheric_carbon_uptake_kg: float
    zone_water_kg: float
    reservoir_kg: float
    transpired_kg: float
    drainage_kg: float


@dataclass(frozen=True)
class NurseryTickResult:
    organs: list[Organ]
    zones: dict[int, float]
    uptake_kg: float
    transpired_kg: float
    drainage_kg: float


def starter_organs() -> list[Organ]:
    """Create two deterministic starter plants with root/stem/leaf cohorts."""
    organs: list[Organ] = []
    organ_id = 1
    for plant_id in (1, 2):
        organs.append(
            Organ(
                organ_id=organ_id,
                plant_id=plant_id,
                parent_id=None,
                kind=OrganKind.ROOT,
                created_tick=0,
                developmental_stage=0,
                length_m=0.12,
                radius_m=0.012,
                surface_area_m2=0.009,
                pools=ResourcePools(
                    structural_carbon_kg=0.020,
                    reserve_carbon_kg=0.010,
                    water_kg=0.050,
                    nitrogen_kg=0.0010,
                    phosphorus_kg=0.00020,
                    potassium_kg=0.00040,
                ),
            )
        )
        root_id = organ_id
        organ_id += 1
        organs.append(
            Organ(
                organ_id=organ_id,
                plant_id=plant_id,
                parent_id=root_id,
                kind=OrganKind.STEM,
                created_tick=0,
                developmental_stage=1,
                length_m=0.18,
                radius_m=0.006,
                surface_area_m2=0.007,
                pools=ResourcePools(
                    structural_carbon_kg=0.012,
                    reserve_carbon_kg=0.0,
                    water_kg=0.010,
                    nitrogen_kg=0.00020,
                    phosphorus_kg=0.00004,
                    potassium_kg=0.00008,
                ),
            )
        )
        stem_id = organ_id
        organ_id += 1
        organs.append(
            Organ(
                organ_id=organ_id,
                plant_id=plant_id,
                parent_id=stem_id,
                kind=OrganKind.LEAF_COHORT,
                created_tick=0,
                developmental_stage=1,
                length_m=0.05,
                radius_m=0.001,
                surface_area_m2=0.060,
                pools=ResourcePools(
                    structural_carbon_kg=0.004,
                    reserve_carbon_kg=0.0,
                    water_kg=0.004,
                    nitrogen_kg=0.00008,
                    phosphorus_kg=0.000016,
                    potassium_kg=0.000032,
                ),
                cohort_count=8,
            )
        )
        organ_id += 1
    validate_topology(organs)
    return organs


def starter_zones() -> dict[int, float]:
    """Create deterministic starter root-zone water for each starter plant."""
    return {plant_id: STARTER_ZONE_WATER_KG for plant_id in (1, 2)}


def advance_nursery(
    organs: list[Organ],
    zones: dict[int, float],
    ticks: int,
) -> NurseryTickResult:
    """Advance starter biology by whole 300-second ticks, deterministically."""
    if ticks < 0:
        raise ValueError("ticks cannot be negative")
    validate_topology(organs)
    validate_zones(organs, zones)
    current = list(organs)
    current_zones = dict(zones)
    uptake = 0.0
    transpired = 0.0
    drainage = 0.0
    for _ in range(ticks):
        for plant_id in sorted({organ.plant_id for organ in current}):
            members = [organ for organ in current if organ.plant_id == plant_id]
            root = next(organ for organ in members if organ.parent_id is None)
            leaf_area = sum(
                organ.surface_area_m2
                for organ in members
                if organ.kind == OrganKind.LEAF_COHORT and organ.alive
            )
            water = advance_zone_water(
                zone_water_kg=current_zones[plant_id],
                capacity_kg=ZONE_CAPACITY_KG,
                root_water_kg=root.pools.water_kg,
                leaf_area_m2=leaf_area,
                dt_seconds=BASE_TICK_SECONDS,
            )
            current_zones[plant_id] = water.zone_water_kg
            transpired += water.transpiration_kg
            drainage += water.drainage_kg
            current = _apply_zone_exchange(
                current, plant_id, water.root_uptake_kg, water.transpiration_kg
            )
            plant_organs = [organ for organ in current if organ.plant_id == plant_id]
            assimilated = assimilate_carbon(
                plant_organs,
                dt_seconds=BASE_TICK_SECONDS,
                par_w_m2=PAR_W_M2,
                parameters=AssimilationParameters(
                    amax_kg_c_m2_s=ASSIMILATION_PARAMETERS.amax_kg_c_m2_s,
                    half_saturation_w_m2=ASSIMILATION_PARAMETERS.half_saturation_w_m2,
                    temperature_factor=ASSIMILATION_PARAMETERS.temperature_factor,
                    water_factor=water.water_stress_factor,
                    nutrient_factor=ASSIMILATION_PARAMETERS.nutrient_factor,
                ),
            )
            uptake += assimilated.atmospheric_carbon_uptake_kg
            by_id = {organ.organ_id: organ for organ in assimilated.organs}
            current = [
                by_id.get(organ.organ_id, organ)
                if organ.plant_id == plant_id
                else organ
                for organ in current
            ]
        demands = _tick_demands(current)
        if demands:
            grown = apply_vegetative_growth(current, demands)
            current = grown.organs
    validate_topology(current)
    validate_zones(current, current_zones)
    return NurseryTickResult(current, current_zones, uptake, transpired, drainage)


def water_plant(
    zones: dict[int, float],
    reservoir_kg: float,
    plant_id: int,
    water_kg: float,
) -> tuple[dict[int, float], float, float]:
    """Transfer finite reservoir water into one plant root zone."""
    if plant_id not in zones:
        raise ValueError("unknown plant")
    if not isinstance(water_kg, float | int) or not math.isfinite(float(water_kg)):
        raise ValueError("water_kg must be finite")
    water_kg = float(water_kg)
    if water_kg <= 0.0:
        raise ValueError("water_kg must be positive")
    if water_kg > MAX_WATER_PER_COMMAND_KG:
        raise ValueError("water_kg exceeds the per-command limit")
    zone_after, reservoir_after, drainage = apply_watering(
        zone_water_kg=zones[plant_id],
        capacity_kg=ZONE_CAPACITY_KG,
        reservoir_kg=reservoir_kg,
        water_kg=water_kg,
    )
    next_zones = dict(zones)
    next_zones[plant_id] = zone_after
    return next_zones, reservoir_after, drainage


def validate_zones(organs: list[Organ], zones: dict[int, float]) -> None:
    plant_ids = {organ.plant_id for organ in organs}
    if set(zones) != plant_ids:
        raise ValueError("zones must exist for every plant exactly once")
    for _plant_id, water_kg in zones.items():
        if not math.isfinite(water_kg):
            raise ValueError("zone water must be finite")
        if water_kg < 0.0 or water_kg > ZONE_CAPACITY_KG:
            raise ValueError("zone water must stay within capacity")


def project_plants(
    organs: list[Organ], zones: dict[int, float]
) -> list[PlantProjection]:
    validate_topology(organs)
    validate_zones(organs, zones)
    projections: list[PlantProjection] = []
    for plant_id in sorted({organ.plant_id for organ in organs}):
        members = [organ for organ in organs if organ.plant_id == plant_id]
        zone_fraction = zones[plant_id] / ZONE_CAPACITY_KG
        projections.append(
            PlantProjection(
                plant_id=plant_id,
                organ_count=len(members),
                leaf_area_m2=sum(
                    organ.surface_area_m2
                    for organ in members
                    if organ.kind == OrganKind.LEAF_COHORT
                ),
                stem_length_m=sum(
                    organ.length_m
                    for organ in members
                    if organ.kind in {OrganKind.STEM, OrganKind.BRANCH}
                ),
                reserve_carbon_kg=sum(organ.pools.reserve_carbon_kg for organ in members),
                structural_carbon_kg=sum(
                    organ.pools.structural_carbon_kg for organ in members
                ),
                zone_water_kg=zones[plant_id],
                water_stress_factor=max(0.0, min(1.0, 0.35 + 0.65 * zone_fraction)),
            )
        )
    return projections


def summarize(
    organs: list[Organ],
    zones: dict[int, float],
    uptake_kg: float = 0.0,
    reservoir_kg: float = 0.0,
    transpired_kg: float = 0.0,
    drainage_kg: float = 0.0,
) -> NurserySummary:
    totals = total_resource_pools(organs)
    return NurserySummary(
        plant_count=len({organ.plant_id for organ in organs}),
        organ_count=len(organs),
        reserve_carbon_kg=totals.reserve_carbon_kg,
        structural_carbon_kg=totals.structural_carbon_kg,
        atmospheric_carbon_uptake_kg=uptake_kg,
        zone_water_kg=sum(zones.values()),
        reservoir_kg=reservoir_kg,
        transpired_kg=transpired_kg,
        drainage_kg=drainage_kg,
    )


def zones_to_payload(zones: dict[int, float]) -> list[dict[str, object]]:
    return [
        {"plant_id": plant_id, "zone_water_kg": zones[plant_id]}
        for plant_id in sorted(zones)
    ]


def zones_from_payload(payload: object, organs: list[Organ]) -> dict[int, float]:
    if not isinstance(payload, list) or not payload:
        return starter_zones_for(organs)
    zones: dict[int, float] = {}
    for entry in payload:
        if not isinstance(entry, dict):
            raise ValueError("nursery zone payload must contain objects")
        try:
            plant_id = int(entry["plant_id"])
            water_kg = float(entry["zone_water_kg"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"invalid nursery zone payload: {exc}") from exc
        if plant_id in zones:
            raise ValueError("nursery zone plant IDs cannot repeat")
        zones[plant_id] = water_kg
    validate_zones(organs, zones)
    return zones


def starter_zones_for(organs: list[Organ]) -> dict[int, float]:
    return {plant_id: STARTER_ZONE_WATER_KG for plant_id in sorted({o.plant_id for o in organs})}


def _apply_zone_exchange(
    organs: list[Organ], plant_id: int, uptake_kg: float, transpiration_kg: float
) -> list[Organ]:
    next_organs: list[Organ] = []
    transpiration_left = transpiration_kg
    for organ in organs:
        if organ.plant_id != plant_id or organ.parent_id is not None:
            next_organs.append(organ)
            continue
        root_water = organ.pools.water_kg + uptake_kg
        root_take = min(root_water, transpiration_left)
        transpiration_left -= root_take
        next_organs.append(
            replace(
                organ,
                pools=replace(
                    organ.pools, water_kg=max(0.0, root_water - root_take)
                ),
            )
        )
    if transpiration_left > 1e-12:
        raise ValueError("transpiration exceeds available plant water")
    validate_topology(next_organs)
    return next_organs


def organs_to_payload(organs: list[Organ]) -> list[dict[str, object]]:
    validate_topology(organs)
    return [
        {
            "organ_id": organ.organ_id,
            "plant_id": organ.plant_id,
            "parent_id": organ.parent_id,
            "kind": organ.kind.value,
            "created_tick": organ.created_tick,
            "developmental_stage": organ.developmental_stage,
            "length_m": organ.length_m,
            "radius_m": organ.radius_m,
            "surface_area_m2": organ.surface_area_m2,
            "pools": {
                "structural_carbon_kg": organ.pools.structural_carbon_kg,
                "reserve_carbon_kg": organ.pools.reserve_carbon_kg,
                "water_kg": organ.pools.water_kg,
                "nitrogen_kg": organ.pools.nitrogen_kg,
                "phosphorus_kg": organ.pools.phosphorus_kg,
                "potassium_kg": organ.pools.potassium_kg,
            },
            "alive": organ.alive,
            "cohort_count": organ.cohort_count,
            "damage_fraction": organ.damage_fraction,
        }
        for organ in organs
    ]


def organs_from_payload(payload: object) -> list[Organ]:
    if not isinstance(payload, list):
        raise ValueError("nursery organs payload must be a list")
    organs: list[Organ] = []
    for entry in payload:
        if not isinstance(entry, dict):
            raise ValueError("nursery organ payload must contain objects")
        pools = entry.get("pools")
        if not isinstance(pools, dict):
            raise ValueError("nursery organ pools must be an object")
        try:
            organs.append(
                Organ(
                    organ_id=int(entry["organ_id"]),
                    plant_id=int(entry["plant_id"]),
                    parent_id=(
                        None if entry.get("parent_id") is None else int(entry["parent_id"])
                    ),
                    kind=OrganKind(str(entry["kind"])),
                    created_tick=int(entry["created_tick"]),
                    developmental_stage=int(entry["developmental_stage"]),
                    length_m=float(entry["length_m"]),
                    radius_m=float(entry["radius_m"]),
                    surface_area_m2=float(entry["surface_area_m2"]),
                    pools=ResourcePools(
                        structural_carbon_kg=float(pools["structural_carbon_kg"]),
                        reserve_carbon_kg=float(pools["reserve_carbon_kg"]),
                        water_kg=float(pools["water_kg"]),
                        nitrogen_kg=float(pools["nitrogen_kg"]),
                        phosphorus_kg=float(pools["phosphorus_kg"]),
                        potassium_kg=float(pools["potassium_kg"]),
                    ),
                    alive=bool(entry["alive"]),
                    cohort_count=int(entry["cohort_count"]),
                    damage_fraction=float(entry["damage_fraction"]),
                )
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"invalid nursery organ payload: {exc}") from exc
    validate_topology(organs)
    return organs


def _tick_demands(organs: list[Organ]) -> list[GrowthDemand]:
    demands: list[GrowthDemand] = []
    for organ in sorted(organs, key=lambda item: item.organ_id):
        if organ.kind not in {OrganKind.STEM, OrganKind.BRANCH} or not organ.alive:
            continue
        root = next(
            item
            for item in organs
            if item.plant_id == organ.plant_id and item.parent_id is None
        )
        carbon = root.pools.reserve_carbon_kg * GROWTH_RESERVE_FRACTION
        if carbon <= 0.0:
            continue
        demands.append(
            GrowthDemand(
                organ_id=organ.organ_id,
                length_increment_m=GROWTH_LENGTH_M_PER_TICK,
                structural_carbon_kg=carbon,
                water_kg=root.pools.water_kg * GROWTH_WATER_FRACTION,
                nitrogen_kg=root.pools.nitrogen_kg * GROWTH_NUTRIENT_FRACTION,
                phosphorus_kg=root.pools.phosphorus_kg * GROWTH_NUTRIENT_FRACTION,
                potassium_kg=root.pools.potassium_kg * GROWTH_NUTRIENT_FRACTION,
            )
        )
    return demands
