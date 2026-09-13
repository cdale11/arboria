"""Organ topology and resource-pool contracts for R1 biology."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum


class BiologyValidationError(ValueError):
    """Raised when biological state violates topology or accounting invariants."""


class OrganKind(StrEnum):
    ROOT = "root"
    STEM = "stem"
    BRANCH = "branch"
    BUD = "bud"
    LEAF_COHORT = "leaf_cohort"
    ROOT_COHORT = "root_cohort"


@dataclass(frozen=True)
class ResourcePools:
    structural_carbon_kg: float
    reserve_carbon_kg: float
    water_kg: float
    nitrogen_kg: float
    phosphorus_kg: float
    potassium_kg: float

    def total_kg(self) -> float:
        return (
            self.structural_carbon_kg
            + self.reserve_carbon_kg
            + self.water_kg
            + self.nitrogen_kg
            + self.phosphorus_kg
            + self.potassium_kg
        )


@dataclass(frozen=True)
class Organ:
    organ_id: int
    plant_id: int
    parent_id: int | None
    kind: OrganKind
    created_tick: int
    developmental_stage: int
    length_m: float
    radius_m: float
    surface_area_m2: float
    pools: ResourcePools
    alive: bool = True
    cohort_count: int = 1
    damage_fraction: float = 0.0


def validate_resource_pools(pools: ResourcePools) -> None:
    for name, value in pools.__dict__.items():
        if not math.isfinite(value):
            raise BiologyValidationError(f"{name} must be finite")
        if value < 0.0:
            raise BiologyValidationError(f"{name} cannot be negative")


def validate_organ(organ: Organ) -> None:
    if organ.organ_id <= 0 or organ.plant_id <= 0:
        raise BiologyValidationError("organ and plant IDs must be positive")
    if organ.parent_id is not None and organ.parent_id <= 0:
        raise BiologyValidationError("parent ID must be positive when present")
    if organ.created_tick < 0 or organ.developmental_stage < 0:
        raise BiologyValidationError("tick and developmental stage cannot be negative")
    for name in ("length_m", "radius_m", "surface_area_m2", "damage_fraction"):
        value = getattr(organ, name)
        if not math.isfinite(value):
            raise BiologyValidationError(f"{name} must be finite")
        if value < 0.0:
            raise BiologyValidationError(f"{name} cannot be negative")
    if organ.damage_fraction > 1.0:
        raise BiologyValidationError("damage_fraction cannot exceed 1")
    if organ.cohort_count < 1:
        raise BiologyValidationError("cohort_count must be at least 1")
    if organ.kind not in {OrganKind.LEAF_COHORT, OrganKind.ROOT_COHORT} and organ.cohort_count != 1:
        raise BiologyValidationError("only cohort organs may have cohort_count above 1")
    validate_resource_pools(organ.pools)


def validate_topology(organs: list[Organ]) -> None:
    ids: set[int] = set()
    by_id: dict[int, Organ] = {}
    roots_by_plant: dict[int, int] = {}
    for organ in organs:
        validate_organ(organ)
        if organ.organ_id in ids:
            raise BiologyValidationError("organ IDs cannot repeat")
        ids.add(organ.organ_id)
        by_id[organ.organ_id] = organ
        if organ.parent_id is None:
            roots_by_plant[organ.plant_id] = roots_by_plant.get(organ.plant_id, 0) + 1
    for plant_id, root_count in roots_by_plant.items():
        if root_count != 1:
            raise BiologyValidationError(f"plant {plant_id} must have exactly one root organ")
    for organ in organs:
        if organ.parent_id is None:
            continue
        parent = by_id.get(organ.parent_id)
        if parent is None:
            raise BiologyValidationError("parent organ must exist")
        if parent.plant_id != organ.plant_id:
            raise BiologyValidationError("organ parent must belong to the same plant")
    visiting: set[int] = set()
    visited: set[int] = set()

    def visit(organ_id: int) -> None:
        if organ_id in visited:
            return
        if organ_id in visiting:
            raise BiologyValidationError("organ parentage must be acyclic")
        visiting.add(organ_id)
        parent_id = by_id[organ_id].parent_id
        if parent_id is not None:
            visit(parent_id)
        visiting.remove(organ_id)
        visited.add(organ_id)

    for organ_id in ids:
        visit(organ_id)


def total_resource_pools(organs: list[Organ]) -> ResourcePools:
    validate_topology(organs)
    return ResourcePools(
        structural_carbon_kg=sum(organ.pools.structural_carbon_kg for organ in organs),
        reserve_carbon_kg=sum(organ.pools.reserve_carbon_kg for organ in organs),
        water_kg=sum(organ.pools.water_kg for organ in organs),
        nitrogen_kg=sum(organ.pools.nitrogen_kg for organ in organs),
        phosphorus_kg=sum(organ.pools.phosphorus_kg for organ in organs),
        potassium_kg=sum(organ.pools.potassium_kg for organ in organs),
    )
