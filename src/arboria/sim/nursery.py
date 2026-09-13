"""Pure R1 nursery state: starter plants and deterministic per-tick biology."""

from __future__ import annotations

from dataclasses import dataclass

from arboria.biology.carbon import AssimilationParameters, assimilate_carbon
from arboria.biology.growth import GrowthDemand, apply_vegetative_growth
from arboria.biology.organs import (
    Organ,
    OrganKind,
    ResourcePools,
    total_resource_pools,
    validate_topology,
)

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
NURSERY_SCHEMA_VERSION = 1
# Fixed per-tick structural demand factors. Small enough to keep starter pools
# positive for many ticks while remaining visible in inspection totals.
GROWTH_RESERVE_FRACTION = 0.001
GROWTH_LENGTH_M_PER_TICK = 0.0005
GROWTH_WATER_FRACTION = 0.01
GROWTH_NUTRIENT_FRACTION = 0.005


@dataclass(frozen=True)
class PlantProjection:
    plant_id: int
    organ_count: int
    leaf_area_m2: float
    stem_length_m: float
    reserve_carbon_kg: float
    structural_carbon_kg: float


@dataclass(frozen=True)
class NurserySummary:
    plant_count: int
    organ_count: int
    reserve_carbon_kg: float
    structural_carbon_kg: float
    atmospheric_carbon_uptake_kg: float


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


def advance_nursery(organs: list[Organ], ticks: int) -> tuple[list[Organ], float]:
    """Advance starter biology by whole 300-second ticks, deterministically."""
    if ticks < 0:
        raise ValueError("ticks cannot be negative")
    validate_topology(organs)
    current = list(organs)
    uptake = 0.0
    for _ in range(ticks):
        assimilated = assimilate_carbon(
            current,
            dt_seconds=BASE_TICK_SECONDS,
            par_w_m2=PAR_W_M2,
            parameters=ASSIMILATION_PARAMETERS,
        )
        current = assimilated.organs
        uptake += assimilated.atmospheric_carbon_uptake_kg
        demands = _tick_demands(current)
        if demands:
            grown = apply_vegetative_growth(current, demands)
            current = grown.organs
    validate_topology(current)
    return current, uptake


def project_plants(organs: list[Organ]) -> list[PlantProjection]:
    validate_topology(organs)
    projections: list[PlantProjection] = []
    for plant_id in sorted({organ.plant_id for organ in organs}):
        members = [organ for organ in organs if organ.plant_id == plant_id]
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
            )
        )
    return projections


def summarize(organs: list[Organ], uptake_kg: float = 0.0) -> NurserySummary:
    totals = total_resource_pools(organs)
    return NurserySummary(
        plant_count=len({organ.plant_id for organ in organs}),
        organ_count=len(organs),
        reserve_carbon_kg=totals.reserve_carbon_kg,
        structural_carbon_kg=totals.structural_carbon_kg,
        atmospheric_carbon_uptake_kg=uptake_kg,
    )


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
