"""Pure R1 nursery state: starter plants and deterministic per-tick biology."""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import Any

from arboria.biology.carbon import AssimilationParameters, assimilate_carbon
from arboria.biology.growth import GrowthDemand, apply_vegetative_growth
from arboria.biology.nutrients import (
    NutrientParameters,
    NutrientZone,
    advance_plant_nutrients,
    advance_stress_damage,
    nutrient_stress_factor,
    validate_nutrient_zone,
)
from arboria.biology.organs import (
    Organ,
    OrganKind,
    ResourcePools,
    total_resource_pools,
    validate_topology,
)
from arboria.biology.species import SpeciesRecord, get_site, get_species
from arboria.biology.water import advance_zone_water, apply_watering

# R1 nursery dynamics are parameterized per starter plant by the species
# catalog. All coefficients remain provisional, not measured constants.
BASE_TICK_SECONDS = 300.0
NURSERY_SCHEMA_VERSION = 4
# Starter composition: plant 1 is greenhouse basil, plant 2 is an outdoor oak.
# The mapping is deterministic code, so no extra persisted state is needed.
SPECIES_BY_PLANT: dict[int, str] = {
    1: "ocimum_basilicum",
    2: "quercus_robur",
}
# Well-mixed R1 root zone per plant. Watering transfers finite reservoir water
# into a zone; above-capacity water drains as an explicit boundary flux.
# Substrate N/P/K is finite per plant with no fertilizer input in R1.
ZONE_CAPACITY_KG = 0.20
STARTER_ZONE_WATER_KG = 0.12
STARTER_RESERVOIR_KG = 2.0
MAX_WATER_PER_COMMAND_KG = 0.05
STARTER_ZONE_NITROGEN_KG = 0.020
STARTER_ZONE_PHOSPHORUS_KG = 0.0040
STARTER_ZONE_POTASSIUM_KG = 0.0080


@dataclass(frozen=True)
class PlantProjection:
    plant_id: int
    species_id: str
    site_id: str
    organ_count: int
    leaf_area_m2: float
    stem_length_m: float
    reserve_carbon_kg: float
    structural_carbon_kg: float
    zone_water_kg: float
    water_stress_factor: float
    alive: bool
    damage_fraction: float
    nutrient_stress_factor: float
    zone_nitrogen_kg: float
    zone_phosphorus_kg: float
    zone_potassium_kg: float


@dataclass(frozen=True)
class NurserySummary:
    plant_count: int
    organ_count: int
    species_ids: tuple[str, ...]
    reserve_carbon_kg: float
    structural_carbon_kg: float
    atmospheric_carbon_uptake_kg: float
    zone_water_kg: float
    reservoir_kg: float
    transpired_kg: float
    drainage_kg: float
    zone_nitrogen_kg: float
    zone_phosphorus_kg: float
    zone_potassium_kg: float
    dead_plant_count: int


@dataclass(frozen=True)
class NurseryTickResult:
    organs: list[Organ]
    zones: dict[int, float]
    nutrient_zones: dict[int, NutrientZone]
    uptake_kg: float
    transpired_kg: float
    drainage_kg: float
    npk_uptake_kg: tuple[float, float, float]


def species_for_plant(plant_id: int) -> SpeciesRecord:
    """Resolve the deterministic catalog species for a starter plant."""
    species_id = SPECIES_BY_PLANT.get(plant_id)
    if species_id is None:
        raise ValueError(f"no species assigned to plant {plant_id}")
    return get_species(species_id)


def starter_species_by_plant() -> dict[int, str]:
    """Create the deterministic starter plant-to-species mapping."""
    return dict(SPECIES_BY_PLANT)


def starter_plant_organs(
    plant_id: int, species_id: str, first_organ_id: int
) -> list[Organ]:
    """Build root/stem/leaf-cohort starters for one plant of a species.

    Geometry is shared across species in R1 (no morphology grammar yet);
    root mobile N/P/K pools start at the species reference values.
    """
    species = get_species(species_id)
    nutrients = species.nutrients
    root_id = first_organ_id
    stem_id = first_organ_id + 1
    leaf_id = first_organ_id + 2
    organs = [
        Organ(
            organ_id=root_id,
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
                nitrogen_kg=nutrients.reference_nitrogen_kg,
                phosphorus_kg=nutrients.reference_phosphorus_kg,
                potassium_kg=nutrients.reference_potassium_kg,
            ),
        ),
        Organ(
            organ_id=stem_id,
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
        ),
        Organ(
            organ_id=leaf_id,
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
        ),
    ]
    validate_topology(organs)
    return organs


def starter_organs() -> list[Organ]:
    """Create two deterministic starter plants with root/stem/leaf cohorts."""
    organs: list[Organ] = []
    organ_id = 1
    for plant_id in (1, 2):
        species_id = SPECIES_BY_PLANT[plant_id]
        organs.extend(starter_plant_organs(plant_id, species_id, organ_id))
        organ_id += 3
    validate_topology(organs)
    return organs


def add_starter_plant(
    organs: list[Organ],
    zones: dict[int, float],
    nutrient_zones: dict[int, NutrientZone],
    species_by_plant: dict[int, str],
    species_id: str,
) -> tuple[list[Organ], dict[int, float], dict[int, NutrientZone], dict[int, str], int]:
    """Add one live starter plant of a catalog species with fresh IDs."""
    validate_topology(organs)
    validate_zones(organs, zones)
    validate_nutrient_zones(organs, nutrient_zones)
    get_species(species_id)
    plant_id = max((organ.plant_id for organ in organs), default=0) + 1
    first_organ_id = max((organ.organ_id for organ in organs), default=0) + 1
    if plant_id in zones or plant_id in nutrient_zones or plant_id in species_by_plant:
        raise ValueError(f"plant {plant_id} already exists")
    next_organs = list(organs) + starter_plant_organs(plant_id, species_id, first_organ_id)
    next_zones = dict(zones)
    next_zones[plant_id] = STARTER_ZONE_WATER_KG
    next_nutrients = dict(nutrient_zones)
    next_nutrients[plant_id] = NutrientZone(
        nitrogen_kg=STARTER_ZONE_NITROGEN_KG,
        phosphorus_kg=STARTER_ZONE_PHOSPHORUS_KG,
        potassium_kg=STARTER_ZONE_POTASSIUM_KG,
    )
    next_mapping = dict(species_by_plant)
    next_mapping[plant_id] = species_id
    validate_topology(next_organs)
    validate_zones(next_organs, next_zones)
    validate_nutrient_zones(next_organs, next_nutrients)
    return next_organs, next_zones, next_nutrients, next_mapping, plant_id


def remove_plant(
    organs: list[Organ],
    zones: dict[int, float],
    nutrient_zones: dict[int, NutrientZone],
    species_by_plant: dict[int, str],
    plant_id: int,
) -> tuple[list[Organ], dict[int, float], dict[int, NutrientZone], dict[int, str], str]:
    """Remove a live plant and its zones; return state plus its species."""
    validate_topology(organs)
    validate_zones(organs, zones)
    validate_nutrient_zones(organs, nutrient_zones)
    members = [organ for organ in organs if organ.plant_id == plant_id]
    if not members:
        raise ValueError("unknown plant")
    root = next(organ for organ in members if organ.parent_id is None)
    if not root.alive:
        raise ValueError("dead plants cannot be sold")
    if plant_id not in species_by_plant:
        raise ValueError(f"no species assigned to plant {plant_id}")
    species_id = species_by_plant[plant_id]
    next_organs = [organ for organ in organs if organ.plant_id != plant_id]
    next_zones = {key: value for key, value in zones.items() if key != plant_id}
    next_nutrients = {
        key: value for key, value in nutrient_zones.items() if key != plant_id
    }
    next_mapping = {
        key: value for key, value in species_by_plant.items() if key != plant_id
    }
    validate_topology(next_organs)
    if next_organs:
        validate_zones(next_organs, next_zones)
        validate_nutrient_zones(next_organs, next_nutrients)
    return next_organs, next_zones, next_nutrients, next_mapping, species_id


def species_to_payload(mapping: dict[int, str]) -> list[dict[str, object]]:
    return [
        {"plant_id": plant_id, "species_id": mapping[plant_id]}
        for plant_id in sorted(mapping)
    ]


def species_from_payload(payload: object, organs: list[Organ]) -> dict[int, str]:
    plant_ids = sorted({organ.plant_id for organ in organs})
    if not isinstance(payload, list) or not payload:
        mapping: dict[int, str] = {}
        for plant_id in plant_ids:
            species_id = SPECIES_BY_PLANT.get(plant_id)
            if species_id is None:
                raise ValueError(f"no species assigned to plant {plant_id}")
            mapping[plant_id] = species_id
        return mapping
    mapping = {}
    for entry in payload:
        if not isinstance(entry, dict):
            raise ValueError("nursery species payload must contain objects")
        try:
            plant_id = int(entry["plant_id"])
            species_id = str(entry["species_id"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"invalid nursery species payload: {exc}") from exc
        if plant_id in mapping:
            raise ValueError("nursery species plant IDs cannot repeat")
        get_species(species_id)
        mapping[plant_id] = species_id
    if sorted(mapping) != plant_ids:
        raise ValueError("nursery species must exist for every plant exactly once")
    return mapping


@dataclass(frozen=True)
class NurseryLoadedState:
    zones: dict[int, float]
    nutrient_zones: dict[int, NutrientZone]
    species_by_plant: dict[int, str]


def load_nursery_state(
    state: dict[str, Any], organs: list[Organ]
) -> NurseryLoadedState:
    """Load versioned nursery state with explicit migration to the current schema.

    Older checkpoint states omit keys introduced by later schema versions and
    fall back to starter values for the recorded plants. States stamped newer
    than this code are rejected rather than guessed at.
    """
    version = state.get("nursery_schema_version", 1)
    if isinstance(version, bool) or not isinstance(version, int):
        raise ValueError("nursery_schema_version must be an integer")
    if version < 1 or version > NURSERY_SCHEMA_VERSION:
        raise ValueError(
            f"unsupported nursery schema version: {version} "
            f"(code supports 1..{NURSERY_SCHEMA_VERSION})"
        )
    return NurseryLoadedState(
        zones=zones_from_payload(state.get("nursery_zones", []), organs),
        nutrient_zones=nutrient_zones_from_payload(
            state.get("nursery_nutrient_zones", []), organs
        ),
        species_by_plant=species_from_payload(
            state.get("nursery_species", []), organs
        ),
    )


def starter_zones() -> dict[int, float]:
    """Create deterministic starter root-zone water for each starter plant."""
    return {plant_id: STARTER_ZONE_WATER_KG for plant_id in (1, 2)}


def starter_nutrient_zones() -> dict[int, NutrientZone]:
    """Create deterministic starter substrate N/P/K for each starter plant."""
    return {
        plant_id: NutrientZone(
            nitrogen_kg=STARTER_ZONE_NITROGEN_KG,
            phosphorus_kg=STARTER_ZONE_PHOSPHORUS_KG,
            potassium_kg=STARTER_ZONE_POTASSIUM_KG,
        )
        for plant_id in (1, 2)
    }


def advance_nursery(
    organs: list[Organ],
    zones: dict[int, float],
    nutrient_zones: dict[int, NutrientZone],
    ticks: int,
    species_by_plant: dict[int, str] | None = None,
) -> NurseryTickResult:
    """Advance starter biology by whole 300-second ticks, deterministically."""
    if ticks < 0:
        raise ValueError("ticks cannot be negative")
    mapping = dict(SPECIES_BY_PLANT if species_by_plant is None else species_by_plant)
    validate_topology(organs)
    validate_zones(organs, zones)
    validate_nutrient_zones(organs, nutrient_zones)
    for plant_id in {organ.plant_id for organ in organs}:
        if plant_id not in mapping:
            raise ValueError(f"no species assigned to plant {plant_id}")
        get_species(mapping[plant_id])
    current = list(organs)
    current_zones = dict(zones)
    current_nutrients = dict(nutrient_zones)
    uptake = 0.0
    transpired = 0.0
    drainage = 0.0
    npk_uptake = [0.0, 0.0, 0.0]
    for _ in range(ticks):
        indices_by_plant = _organ_indices_by_plant(current)
        params_by_plant: dict[int, SpeciesRecord] = {}
        stress_by_plant: dict[int, float] = {}
        for plant_id in sorted({organ.plant_id for organ in current}):
            members = [organ for organ in current if organ.plant_id == plant_id]
            root = next(organ for organ in members if organ.parent_id is None)
            if not root.alive:
                continue
            species = get_species(mapping[plant_id])
            params_by_plant[plant_id] = species
            site = get_site(species.site_id)
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
                conductance_kg_s=species.conductance_kg_s,
                transpiration_kg_s_m2=species.transpiration_kg_s_m2,
            )
            current_zones[plant_id] = water.zone_water_kg
            transpired += water.transpiration_kg
            drainage += water.drainage_kg
            current = _apply_zone_exchange(
                current,
                plant_id,
                water.root_uptake_kg,
                water.transpiration_kg,
                indices_by_plant[plant_id],
            )
            live_root = next(
                organ
                for organ in current
                if organ.plant_id == plant_id and organ.parent_id is None
            )
            nutrients = advance_plant_nutrients(
                zone=current_nutrients[plant_id],
                root_nitrogen_kg=live_root.pools.nitrogen_kg,
                root_phosphorus_kg=live_root.pools.phosphorus_kg,
                root_potassium_kg=live_root.pools.potassium_kg,
                dt_seconds=BASE_TICK_SECONDS,
                parameters=species.nutrients,
            )
            current_nutrients[plant_id] = nutrients.zone
            npk_uptake[0] += nutrients.uptake_nitrogen_kg
            npk_uptake[1] += nutrients.uptake_phosphorus_kg
            npk_uptake[2] += nutrients.uptake_potassium_kg
            current = _apply_nutrient_uptake(
                current,
                plant_id,
                nutrients.root_nitrogen_kg,
                nutrients.root_phosphorus_kg,
                nutrients.root_potassium_kg,
                indices_by_plant[plant_id],
            )
            plant_organs = [organ for organ in current if organ.plant_id == plant_id]
            assimilated = assimilate_carbon(
                plant_organs,
                dt_seconds=BASE_TICK_SECONDS,
                par_w_m2=site.par_w_m2,
                parameters=AssimilationParameters(
                    amax_kg_c_m2_s=species.amax_kg_c_m2_s,
                    half_saturation_w_m2=species.half_saturation_w_m2,
                    temperature_factor=species.temperature_factor,
                    water_factor=water.water_stress_factor,
                    nutrient_factor=nutrients.nutrient_stress_factor,
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
            stress_by_plant[plant_id] = min(
                water.water_stress_factor, nutrients.nutrient_stress_factor
            )
        demands = _tick_demands(current, params_by_plant)
        if demands:
            grown = apply_vegetative_growth(current, demands)
            current = grown.organs
        for plant_id, combined in stress_by_plant.items():
            current = _apply_stress_damage(
                current,
                plant_id,
                combined,
                params_by_plant[plant_id].nutrients,
                indices_by_plant[plant_id],
            )
    validate_topology(current)
    validate_zones(current, current_zones)
    validate_nutrient_zones(current, current_nutrients)
    return NurseryTickResult(
        current, current_zones, current_nutrients, uptake, transpired, drainage,
        (npk_uptake[0], npk_uptake[1], npk_uptake[2]),
    )


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


def validate_nutrient_zones(
    organs: list[Organ], nutrient_zones: dict[int, NutrientZone]
) -> None:
    plant_ids = {organ.plant_id for organ in organs}
    if set(nutrient_zones) != plant_ids:
        raise ValueError("nutrient zones must exist for every plant exactly once")
    for zone in nutrient_zones.values():
        if not isinstance(zone, NutrientZone):
            raise ValueError("nutrient zones must be NutrientZone records")
        validate_nutrient_zone(zone)


def project_plants(
    organs: list[Organ],
    zones: dict[int, float],
    nutrient_zones: dict[int, NutrientZone],
    species_by_plant: dict[int, str] | None = None,
) -> list[PlantProjection]:
    validate_topology(organs)
    validate_zones(organs, zones)
    validate_nutrient_zones(organs, nutrient_zones)
    mapping = dict(SPECIES_BY_PLANT if species_by_plant is None else species_by_plant)
    projections: list[PlantProjection] = []
    for plant_id in sorted({organ.plant_id for organ in organs}):
        members = [organ for organ in organs if organ.plant_id == plant_id]
        root = next(organ for organ in members if organ.parent_id is None)
        zone_fraction = zones[plant_id] / ZONE_CAPACITY_KG
        nutrient_zone = nutrient_zones[plant_id]
        if plant_id not in mapping:
            raise ValueError(f"no species assigned to plant {plant_id}")
        species = get_species(mapping[plant_id])
        projections.append(
            PlantProjection(
                plant_id=plant_id,
                species_id=species.species_id,
                site_id=species.site_id,
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
                alive=root.alive,
                damage_fraction=max(organ.damage_fraction for organ in members),
                nutrient_stress_factor=nutrient_stress_factor(
                    root_nitrogen_kg=root.pools.nitrogen_kg,
                    root_phosphorus_kg=root.pools.phosphorus_kg,
                    root_potassium_kg=root.pools.potassium_kg,
                    parameters=species.nutrients,
                ),
                zone_nitrogen_kg=nutrient_zone.nitrogen_kg,
                zone_phosphorus_kg=nutrient_zone.phosphorus_kg,
                zone_potassium_kg=nutrient_zone.potassium_kg,
            )
        )
    return projections


def summarize(
    organs: list[Organ],
    zones: dict[int, float],
    nutrient_zones: dict[int, NutrientZone],
    uptake_kg: float = 0.0,
    reservoir_kg: float = 0.0,
    transpired_kg: float = 0.0,
    drainage_kg: float = 0.0,
    species_by_plant: dict[int, str] | None = None,
) -> NurserySummary:
    totals = total_resource_pools(organs)
    roots = {organ.plant_id: organ for organ in organs if organ.parent_id is None}
    mapping = dict(SPECIES_BY_PLANT if species_by_plant is None else species_by_plant)
    for plant_id in roots:
        if plant_id not in mapping:
            raise ValueError(f"no species assigned to plant {plant_id}")
    return NurserySummary(
        plant_count=len({organ.plant_id for organ in organs}),
        organ_count=len(organs),
        species_ids=tuple(sorted({mapping[plant_id] for plant_id in roots})),
        reserve_carbon_kg=totals.reserve_carbon_kg,
        structural_carbon_kg=totals.structural_carbon_kg,
        atmospheric_carbon_uptake_kg=uptake_kg,
        zone_water_kg=sum(zones.values()),
        reservoir_kg=reservoir_kg,
        transpired_kg=transpired_kg,
        drainage_kg=drainage_kg,
        zone_nitrogen_kg=sum(zone.nitrogen_kg for zone in nutrient_zones.values()),
        zone_phosphorus_kg=sum(zone.phosphorus_kg for zone in nutrient_zones.values()),
        zone_potassium_kg=sum(zone.potassium_kg for zone in nutrient_zones.values()),
        dead_plant_count=sum(1 for root in roots.values() if not root.alive),
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


def starter_nutrient_zones_for(organs: list[Organ]) -> dict[int, NutrientZone]:
    return {
        plant_id: NutrientZone(
            nitrogen_kg=STARTER_ZONE_NITROGEN_KG,
            phosphorus_kg=STARTER_ZONE_PHOSPHORUS_KG,
            potassium_kg=STARTER_ZONE_POTASSIUM_KG,
        )
        for plant_id in sorted({o.plant_id for o in organs})
    }


def nutrient_zones_to_payload(
    nutrient_zones: dict[int, NutrientZone],
) -> list[dict[str, object]]:
    return [
        {
            "plant_id": plant_id,
            "nitrogen_kg": nutrient_zones[plant_id].nitrogen_kg,
            "phosphorus_kg": nutrient_zones[plant_id].phosphorus_kg,
            "potassium_kg": nutrient_zones[plant_id].potassium_kg,
        }
        for plant_id in sorted(nutrient_zones)
    ]


def nutrient_zones_from_payload(
    payload: object, organs: list[Organ]
) -> dict[int, NutrientZone]:
    if not isinstance(payload, list) or not payload:
        return starter_nutrient_zones_for(organs)
    nutrient_zones: dict[int, NutrientZone] = {}
    for entry in payload:
        if not isinstance(entry, dict):
            raise ValueError("nursery nutrient zone payload must contain objects")
        try:
            plant_id = int(entry["plant_id"])
            zone = NutrientZone(
                nitrogen_kg=float(entry["nitrogen_kg"]),
                phosphorus_kg=float(entry["phosphorus_kg"]),
                potassium_kg=float(entry["potassium_kg"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"invalid nursery nutrient zone payload: {exc}") from exc
        if plant_id in nutrient_zones:
            raise ValueError("nursery nutrient zone plant IDs cannot repeat")
        nutrient_zones[plant_id] = zone
    validate_nutrient_zones(organs, nutrient_zones)
    return nutrient_zones


def _apply_nutrient_uptake(
    organs: list[Organ],
    plant_id: int,
    nitrogen_kg: float,
    phosphorus_kg: float,
    potassium_kg: float,
    indices: list[int],
) -> list[Organ]:
    for index in indices:
        organ = organs[index]
        if organ.parent_id is None:
            organs[index] = replace(
                organ,
                pools=replace(
                    organ.pools,
                    nitrogen_kg=nitrogen_kg,
                    phosphorus_kg=phosphorus_kg,
                    potassium_kg=potassium_kg,
                ),
            )
            break
    return organs


def _apply_stress_damage(
    organs: list[Organ],
    plant_id: int,
    combined_stress: float,
    parameters: NutrientParameters,
    indices: list[int],
) -> list[Organ]:
    for index in indices:
        organ = organs[index]
        if not organ.alive:
            continue
        damage = advance_stress_damage(
            damage_fraction=organ.damage_fraction,
            alive=True,
            combined_stress_factor=combined_stress,
            dt_seconds=BASE_TICK_SECONDS,
            parameters=parameters,
        )
        organs[index] = (
            replace(organ, damage_fraction=damage.damage_fraction, alive=damage.alive)
        )
    return organs


def _apply_zone_exchange(
    organs: list[Organ],
    plant_id: int,
    uptake_kg: float,
    transpiration_kg: float,
    indices: list[int],
) -> list[Organ]:
    transpiration_left = transpiration_kg
    for index in indices:
        organ = organs[index]
        if organ.parent_id is not None:
            continue
        root_water = organ.pools.water_kg + uptake_kg
        root_take = min(root_water, transpiration_left)
        transpiration_left -= root_take
        organs[index] = (
            replace(
                organ,
                pools=replace(
                    organ.pools, water_kg=max(0.0, root_water - root_take)
                ),
            )
        )
        break
    if transpiration_left > 1e-12:
        raise ValueError("transpiration exceeds available plant water")
    return organs


def _organ_indices_by_plant(organs: list[Organ]) -> dict[int, list[int]]:
    indices: dict[int, list[int]] = {}
    for index, organ in enumerate(organs):
        indices.setdefault(organ.plant_id, []).append(index)
    return indices


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


def _tick_demands(
    organs: list[Organ], params_by_plant: dict[int, SpeciesRecord]
) -> list[GrowthDemand]:
    demands: list[GrowthDemand] = []
    roots = {organ.plant_id: organ for organ in organs if organ.parent_id is None}
    for organ in sorted(organs, key=lambda item: item.organ_id):
        if organ.kind not in {OrganKind.STEM, OrganKind.BRANCH} or not organ.alive:
            continue
        root = roots.get(organ.plant_id)
        species = params_by_plant.get(organ.plant_id)
        if root is None or not root.alive or species is None:
            continue
        carbon = root.pools.reserve_carbon_kg * species.growth_reserve_fraction
        if carbon <= 0.0:
            continue
        demands.append(
            GrowthDemand(
                organ_id=organ.organ_id,
                length_increment_m=species.growth_length_m_per_tick,
                structural_carbon_kg=carbon,
                water_kg=root.pools.water_kg * species.growth_water_fraction,
                nitrogen_kg=root.pools.nitrogen_kg * species.growth_nutrient_fraction,
                phosphorus_kg=root.pools.phosphorus_kg * species.growth_nutrient_fraction,
                potassium_kg=root.pools.potassium_kg * species.growth_nutrient_fraction,
            )
        )
    return demands
