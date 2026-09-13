import pytest

from arboria.biology.growth import GrowthDemand, apply_vegetative_growth
from arboria.biology.organs import Organ, OrganKind, ResourcePools, total_resource_pools


def pools(
    *,
    structural_carbon_kg: float = 1.0,
    reserve_carbon_kg: float = 1.0,
    water_kg: float = 2.0,
    nitrogen_kg: float = 0.1,
    phosphorus_kg: float = 0.02,
    potassium_kg: float = 0.03,
) -> ResourcePools:
    return ResourcePools(
        structural_carbon_kg,
        reserve_carbon_kg,
        water_kg,
        nitrogen_kg,
        phosphorus_kg,
        potassium_kg,
    )


def organ(
    organ_id: int,
    *,
    parent_id: int | None = None,
    kind: OrganKind = OrganKind.STEM,
    resource_pools: ResourcePools | None = None,
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
        surface_area_m2=0.01,
        pools=resource_pools or pools(),
    )


def demand(organ_id: int) -> GrowthDemand:
    return GrowthDemand(
        organ_id=organ_id,
        length_increment_m=0.2,
        structural_carbon_kg=0.25,
        water_kg=0.4,
        nitrogen_kg=0.02,
        phosphorus_kg=0.004,
        potassium_kg=0.006,
    )


def test_growth_debits_root_reserves_and_extends_existing_organ() -> None:
    organs = [organ(1, kind=OrganKind.ROOT), organ(2, parent_id=1)]

    result = apply_vegetative_growth(organs, [demand(2)])

    root = result.organs[0]
    stem = result.organs[1]
    assert result.applied_fraction == 1.0
    assert stem.length_m == pytest.approx(0.3)
    assert stem.pools.structural_carbon_kg == pytest.approx(1.25)
    assert root.pools.reserve_carbon_kg == pytest.approx(0.75)
    assert root.pools.water_kg == pytest.approx(1.6)
    assert len(result.organs) == len(organs)


def test_growth_scales_by_limiting_resource_without_negative_pools() -> None:
    organs = [
        organ(1, kind=OrganKind.ROOT, resource_pools=pools(reserve_carbon_kg=0.125)),
        organ(2, parent_id=1),
    ]

    result = apply_vegetative_growth(organs, [demand(2)])

    assert result.applied_fraction == 0.5
    assert result.unmet_fraction == 0.5
    assert result.organs[1].length_m == pytest.approx(0.2)
    assert result.organs[0].pools.reserve_carbon_kg == pytest.approx(0.0)


def test_growth_preserves_total_material_accounting_between_organs() -> None:
    organs = [organ(1, kind=OrganKind.ROOT), organ(2, parent_id=1)]
    before = total_resource_pools(organs)

    result = apply_vegetative_growth(organs, [demand(2)])
    after = total_resource_pools(result.organs)

    assert after.structural_carbon_kg == pytest.approx(before.structural_carbon_kg + 0.25)
    assert after.reserve_carbon_kg == pytest.approx(before.reserve_carbon_kg - 0.25)
    assert after.water_kg == pytest.approx(before.water_kg)
    assert after.nitrogen_kg == pytest.approx(before.nitrogen_kg)
    assert after.phosphorus_kg == pytest.approx(before.phosphorus_kg)
    assert after.potassium_kg == pytest.approx(before.potassium_kg)


def test_growth_rejects_leaf_cohort_targets() -> None:
    organs = [
        organ(1, kind=OrganKind.ROOT),
        organ(2, parent_id=1, kind=OrganKind.LEAF_COHORT),
    ]

    with pytest.raises(ValueError, match="structural organ"):
        apply_vegetative_growth(organs, [demand(2)])


def test_growth_rejects_negative_demands() -> None:
    organs = [organ(1, kind=OrganKind.ROOT), organ(2, parent_id=1)]

    with pytest.raises(ValueError, match="finite and nonnegative"):
        apply_vegetative_growth(
            organs,
            [
                GrowthDemand(
                    organ_id=2,
                    length_increment_m=-0.1,
                    structural_carbon_kg=0.0,
                    water_kg=0.0,
                    nitrogen_kg=0.0,
                    phosphorus_kg=0.0,
                    potassium_kg=0.0,
                )
            ],
        )
