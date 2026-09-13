"""Resource-bounded vegetative growth kernels for R1 biology."""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

from arboria.biology.organs import Organ, OrganKind, ResourcePools, validate_topology


@dataclass(frozen=True)
class GrowthDemand:
    organ_id: int
    length_increment_m: float
    structural_carbon_kg: float
    water_kg: float
    nitrogen_kg: float
    phosphorus_kg: float
    potassium_kg: float


@dataclass(frozen=True)
class GrowthResult:
    organs: list[Organ]
    applied_fraction: float
    debited: ResourcePools
    unmet_fraction: float


def apply_vegetative_growth(organs: list[Organ], demands: list[GrowthDemand]) -> GrowthResult:
    """Apply existing-organ growth using the most limiting available resource.

    The kernel does not create organs. It debits reserve carbon and mineral/water
    pools from the plant root organ, then scales all requested increments by the
    same limiting fraction so resource accounting remains explicit.
    """
    validate_topology(organs)
    by_id = {organ.organ_id: organ for organ in organs}
    demand_by_id = {demand.organ_id: demand for demand in demands}
    if len(demand_by_id) != len(demands):
        raise ValueError("growth demands cannot repeat organ IDs")
    for demand in demands:
        _validate_demand(demand)
        organ = by_id.get(demand.organ_id)
        if organ is None:
            raise ValueError("growth demand target organ must exist")
        if organ.kind not in {OrganKind.STEM, OrganKind.BRANCH, OrganKind.ROOT}:
            raise ValueError("growth demand target must be a structural organ")
    requested = ResourcePools(
        structural_carbon_kg=sum(d.structural_carbon_kg for d in demands),
        reserve_carbon_kg=0.0,
        water_kg=sum(d.water_kg for d in demands),
        nitrogen_kg=sum(d.nitrogen_kg for d in demands),
        phosphorus_kg=sum(d.phosphorus_kg for d in demands),
        potassium_kg=sum(d.potassium_kg for d in demands),
    )
    if requested.total_kg() == 0.0:
        return GrowthResult(
            organs=list(organs),
            applied_fraction=0.0,
            debited=_zero(),
            unmet_fraction=1.0,
        )
    roots = {organ.plant_id: organ for organ in organs if organ.parent_id is None}
    fraction = 1.0
    for plant_id, root in roots.items():
        plant_demands = [d for d in demands if by_id[d.organ_id].plant_id == plant_id]
        plant_requested = ResourcePools(
            structural_carbon_kg=sum(d.structural_carbon_kg for d in plant_demands),
            reserve_carbon_kg=0.0,
            water_kg=sum(d.water_kg for d in plant_demands),
            nitrogen_kg=sum(d.nitrogen_kg for d in plant_demands),
            phosphorus_kg=sum(d.phosphorus_kg for d in plant_demands),
            potassium_kg=sum(d.potassium_kg for d in plant_demands),
        )
        fraction = min(fraction, _available_fraction(root.pools, plant_requested))
    next_organs: list[Organ] = []
    debited = _zero()
    for organ in organs:
        organ_demand = demand_by_id.get(organ.organ_id)
        if organ_demand is None:
            if organ.parent_id is None:
                plant_debit = _plant_debit(organs, by_id, demand_by_id, organ.plant_id, fraction)
                organ = replace(organ, pools=_subtract(organ.pools, plant_debit))
            next_organs.append(organ)
            continue
        increment = organ_demand.length_increment_m * fraction
        grown = replace(
            organ,
            length_m=organ.length_m + increment,
            pools=replace(
                organ.pools,
                structural_carbon_kg=organ.pools.structural_carbon_kg
                + organ_demand.structural_carbon_kg * fraction,
                water_kg=organ.pools.water_kg + organ_demand.water_kg * fraction,
                nitrogen_kg=organ.pools.nitrogen_kg + organ_demand.nitrogen_kg * fraction,
                phosphorus_kg=organ.pools.phosphorus_kg + organ_demand.phosphorus_kg * fraction,
                potassium_kg=organ.pools.potassium_kg + organ_demand.potassium_kg * fraction,
            ),
        )
        next_organs.append(grown)
        debited = _add_debit(debited, organ_demand, fraction)
    validate_topology(next_organs)
    return GrowthResult(next_organs, fraction, debited, 1.0 - fraction)


def _validate_demand(demand: GrowthDemand) -> None:
    for value in demand.__dict__.values():
        if isinstance(value, float) and (not math.isfinite(value) or value < 0.0):
            raise ValueError("growth demand values must be finite and nonnegative")
    if demand.organ_id <= 0:
        raise ValueError("growth demand organ_id must be positive")


def _available_fraction(available: ResourcePools, requested: ResourcePools) -> float:
    limits = [1.0]
    pairs = [
        (available.reserve_carbon_kg, requested.structural_carbon_kg),
        (available.water_kg, requested.water_kg),
        (available.nitrogen_kg, requested.nitrogen_kg),
        (available.phosphorus_kg, requested.phosphorus_kg),
        (available.potassium_kg, requested.potassium_kg),
    ]
    for have, need in pairs:
        if need > 0.0:
            limits.append(have / need)
    return max(0.0, min(limits))


def _plant_debit(
    organs: list[Organ],
    by_id: dict[int, Organ],
    demand_by_id: dict[int, GrowthDemand],
    plant_id: int,
    fraction: float,
) -> ResourcePools:
    debit = _zero()
    for organ in organs:
        demand = demand_by_id.get(organ.organ_id)
        if demand is not None and by_id[demand.organ_id].plant_id == plant_id:
            debit = _add_debit(debit, demand, fraction)
    return debit


def _add_debit(total: ResourcePools, demand: GrowthDemand, fraction: float) -> ResourcePools:
    return ResourcePools(
        structural_carbon_kg=total.structural_carbon_kg,
        reserve_carbon_kg=total.reserve_carbon_kg + demand.structural_carbon_kg * fraction,
        water_kg=total.water_kg + demand.water_kg * fraction,
        nitrogen_kg=total.nitrogen_kg + demand.nitrogen_kg * fraction,
        phosphorus_kg=total.phosphorus_kg + demand.phosphorus_kg * fraction,
        potassium_kg=total.potassium_kg + demand.potassium_kg * fraction,
    )


def _subtract(left: ResourcePools, right: ResourcePools) -> ResourcePools:
    return ResourcePools(
        structural_carbon_kg=left.structural_carbon_kg,
        reserve_carbon_kg=left.reserve_carbon_kg - right.reserve_carbon_kg,
        water_kg=left.water_kg - right.water_kg,
        nitrogen_kg=left.nitrogen_kg - right.nitrogen_kg,
        phosphorus_kg=left.phosphorus_kg - right.phosphorus_kg,
        potassium_kg=left.potassium_kg - right.potassium_kg,
    )


def _zero() -> ResourcePools:
    return ResourcePools(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
