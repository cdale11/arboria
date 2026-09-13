import pytest

from arboria.biology.carbon import AssimilationParameters, assimilate_carbon
from arboria.biology.organs import Organ, OrganKind, ResourcePools, total_resource_pools


def pools(reserve_carbon_kg: float = 0.0) -> ResourcePools:
    return ResourcePools(
        structural_carbon_kg=1.0,
        reserve_carbon_kg=reserve_carbon_kg,
        water_kg=1.0,
        nitrogen_kg=0.01,
        phosphorus_kg=0.001,
        potassium_kg=0.002,
    )


def organ(
    organ_id: int,
    *,
    parent_id: int | None = None,
    kind: OrganKind = OrganKind.STEM,
    surface_area_m2: float = 0.01,
    alive: bool = True,
) -> Organ:
    return Organ(
        organ_id=organ_id,
        plant_id=1,
        parent_id=parent_id,
        kind=kind,
        created_tick=0,
        developmental_stage=0,
        length_m=0.1,
        radius_m=0.01,
        surface_area_m2=surface_area_m2,
        pools=pools(),
        alive=alive,
        cohort_count=10 if kind == OrganKind.LEAF_COHORT else 1,
    )


def params() -> AssimilationParameters:
    return AssimilationParameters(
        amax_kg_c_m2_s=1e-6,
        half_saturation_w_m2=100.0,
        temperature_factor=1.0,
        water_factor=1.0,
        nutrient_factor=1.0,
    )


def test_assimilation_adds_leaf_carbon_to_root_reserves() -> None:
    organs = [
        organ(1, kind=OrganKind.ROOT),
        organ(2, parent_id=1, kind=OrganKind.LEAF_COHORT, surface_area_m2=2.0),
    ]

    result = assimilate_carbon(organs, dt_seconds=10.0, par_w_m2=100.0, parameters=params())

    assert result.atmospheric_carbon_uptake_kg == pytest.approx(1e-5)
    assert result.reserve_carbon_added_kg == pytest.approx(1e-5)
    assert result.organs[0].pools.reserve_carbon_kg == pytest.approx(1e-5)


def test_assimilation_uses_bounded_stress_factors() -> None:
    organs = [
        organ(1, kind=OrganKind.ROOT),
        organ(2, parent_id=1, kind=OrganKind.LEAF_COHORT, surface_area_m2=2.0),
    ]
    stressed = AssimilationParameters(1e-6, 100.0, 0.5, 0.5, 0.5)

    result = assimilate_carbon(organs, dt_seconds=10.0, par_w_m2=100.0, parameters=stressed)

    assert result.reserve_carbon_added_kg == pytest.approx(1.25e-6)


def test_assimilation_does_not_use_dead_or_missing_leaves() -> None:
    organs = [
        organ(1, kind=OrganKind.ROOT),
        organ(2, parent_id=1, kind=OrganKind.LEAF_COHORT, surface_area_m2=2.0, alive=False),
    ]

    result = assimilate_carbon(organs, dt_seconds=10.0, par_w_m2=100.0, parameters=params())

    assert result.reserve_carbon_added_kg == 0.0
    assert result.organs[0].pools.reserve_carbon_kg == 0.0


def test_assimilation_keeps_noncarbon_materials_unchanged() -> None:
    organs = [
        organ(1, kind=OrganKind.ROOT),
        organ(2, parent_id=1, kind=OrganKind.LEAF_COHORT, surface_area_m2=2.0),
    ]
    before = total_resource_pools(organs)

    result = assimilate_carbon(organs, dt_seconds=10.0, par_w_m2=100.0, parameters=params())
    after = total_resource_pools(result.organs)

    assert after.reserve_carbon_kg == pytest.approx(before.reserve_carbon_kg + 1e-5)
    assert after.water_kg == before.water_kg
    assert after.nitrogen_kg == before.nitrogen_kg
    assert after.phosphorus_kg == before.phosphorus_kg
    assert after.potassium_kg == before.potassium_kg


def test_assimilation_rejects_invalid_inputs() -> None:
    organs = [organ(1, kind=OrganKind.ROOT)]
    with pytest.raises(ValueError, match="cannot be negative"):
        assimilate_carbon(organs, dt_seconds=-1.0, par_w_m2=100.0, parameters=params())
    with pytest.raises(ValueError, match="cannot exceed 1"):
        assimilate_carbon(
            organs,
            dt_seconds=1.0,
            par_w_m2=100.0,
            parameters=AssimilationParameters(1e-6, 100.0, 1.1, 1.0, 1.0),
        )
