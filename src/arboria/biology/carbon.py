"""Bounded light-driven carbon assimilation for R1 biology."""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

from arboria.biology.organs import Organ, OrganKind, validate_topology


@dataclass(frozen=True)
class AssimilationParameters:
    amax_kg_c_m2_s: float
    half_saturation_w_m2: float
    temperature_factor: float
    water_factor: float
    nutrient_factor: float


@dataclass(frozen=True)
class AssimilationResult:
    organs: list[Organ]
    atmospheric_carbon_uptake_kg: float
    reserve_carbon_added_kg: float


def assimilate_carbon(
    organs: list[Organ],
    *,
    dt_seconds: float,
    par_w_m2: float,
    parameters: AssimilationParameters,
) -> AssimilationResult:
    """Add reserve carbon to each plant root from leaf-cohort photosynthesis.

    This is the explicitly provisional saturating R1 response documented in
    `docs/biology.md`, not a Farquhar/CAM/C4 model.
    """
    validate_topology(organs)
    _validate_inputs(dt_seconds, par_w_m2, parameters)
    if dt_seconds == 0.0 or par_w_m2 == 0.0:
        return AssimilationResult(list(organs), 0.0, 0.0)
    response = par_w_m2 / (par_w_m2 + parameters.half_saturation_w_m2)
    stress = parameters.temperature_factor * parameters.water_factor * parameters.nutrient_factor
    carbon_by_plant: dict[int, float] = {}
    for organ in organs:
        if organ.kind != OrganKind.LEAF_COHORT or not organ.alive:
            continue
        carbon = (
            organ.surface_area_m2
            * parameters.amax_kg_c_m2_s
            * response
            * stress
            * dt_seconds
        )
        carbon_by_plant[organ.plant_id] = carbon_by_plant.get(organ.plant_id, 0.0) + carbon
    if not carbon_by_plant:
        return AssimilationResult(list(organs), 0.0, 0.0)
    next_organs: list[Organ] = []
    total = 0.0
    for organ in organs:
        addition = carbon_by_plant.get(organ.plant_id, 0.0) if organ.parent_id is None else 0.0
        if addition > 0.0:
            total += addition
            organ = replace(
                organ,
                pools=replace(
                    organ.pools,
                    reserve_carbon_kg=organ.pools.reserve_carbon_kg + addition,
                ),
            )
        next_organs.append(organ)
    validate_topology(next_organs)
    return AssimilationResult(next_organs, total, total)


def _validate_inputs(
    dt_seconds: float, par_w_m2: float, parameters: AssimilationParameters
) -> None:
    for name, value in {
        "dt_seconds": dt_seconds,
        "par_w_m2": par_w_m2,
        "amax_kg_c_m2_s": parameters.amax_kg_c_m2_s,
        "half_saturation_w_m2": parameters.half_saturation_w_m2,
        "temperature_factor": parameters.temperature_factor,
        "water_factor": parameters.water_factor,
        "nutrient_factor": parameters.nutrient_factor,
    }.items():
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
        if value < 0.0:
            raise ValueError(f"{name} cannot be negative")
    if parameters.half_saturation_w_m2 <= 0.0:
        raise ValueError("half_saturation_w_m2 must be positive")
    for name, value in {
        "temperature_factor": parameters.temperature_factor,
        "water_factor": parameters.water_factor,
        "nutrient_factor": parameters.nutrient_factor,
    }.items():
        if value > 1.0:
            raise ValueError(f"{name} cannot exceed 1")
