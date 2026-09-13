import pytest

from arboria.biology.organs import (
    BiologyValidationError,
    Organ,
    OrganKind,
    ResourcePools,
    total_resource_pools,
    validate_resource_pools,
    validate_topology,
)


def pools(
    *,
    structural_carbon_kg: float = 1.0,
    reserve_carbon_kg: float = 0.1,
    water_kg: float = 2.0,
    nitrogen_kg: float = 0.01,
    phosphorus_kg: float = 0.001,
    potassium_kg: float = 0.002,
) -> ResourcePools:
    return ResourcePools(
        structural_carbon_kg=structural_carbon_kg,
        reserve_carbon_kg=reserve_carbon_kg,
        water_kg=water_kg,
        nitrogen_kg=nitrogen_kg,
        phosphorus_kg=phosphorus_kg,
        potassium_kg=potassium_kg,
    )


def organ(
    organ_id: int,
    *,
    plant_id: int = 1,
    parent_id: int | None = None,
    kind: OrganKind = OrganKind.STEM,
    cohort_count: int = 1,
) -> Organ:
    return Organ(
        organ_id=organ_id,
        plant_id=plant_id,
        parent_id=parent_id,
        kind=kind,
        created_tick=0,
        developmental_stage=0,
        length_m=0.1,
        radius_m=0.01,
        surface_area_m2=0.01,
        pools=pools(),
        cohort_count=cohort_count,
    )


def test_valid_topology_allows_one_root_and_children() -> None:
    validate_topology(
        [
            organ(1, kind=OrganKind.ROOT),
            organ(2, parent_id=1),
            organ(3, parent_id=2, kind=OrganKind.LEAF_COHORT, cohort_count=12),
        ]
    )


def test_topology_rejects_duplicate_stable_ids() -> None:
    with pytest.raises(BiologyValidationError, match="cannot repeat"):
        validate_topology([organ(1, kind=OrganKind.ROOT), organ(1, parent_id=1)])


def test_topology_rejects_cycles() -> None:
    with pytest.raises(BiologyValidationError, match="acyclic"):
        validate_topology(
            [
                organ(1, kind=OrganKind.ROOT),
                organ(2, parent_id=3),
                organ(3, parent_id=2),
            ]
        )


def test_topology_rejects_cross_plant_parentage() -> None:
    with pytest.raises(BiologyValidationError, match="same plant"):
        validate_topology(
            [
                organ(1, plant_id=1, kind=OrganKind.ROOT),
                organ(2, plant_id=2, kind=OrganKind.ROOT),
                organ(3, plant_id=2, parent_id=1),
            ]
        )


def test_only_cohort_organs_can_have_aggregate_count() -> None:
    with pytest.raises(BiologyValidationError, match="only cohort organs"):
        validate_topology([organ(1, kind=OrganKind.ROOT), organ(2, parent_id=1, cohort_count=2)])


def test_resource_pools_reject_negative_or_nonfinite_values() -> None:
    with pytest.raises(BiologyValidationError, match="cannot be negative"):
        validate_resource_pools(pools(water_kg=-1.0))
    with pytest.raises(BiologyValidationError, match="must be finite"):
        validate_resource_pools(pools(reserve_carbon_kg=float("inf")))


def test_total_resource_pools_keep_materials_separate() -> None:
    first = organ(1, kind=OrganKind.ROOT)
    second = organ(2, parent_id=1, kind=OrganKind.LEAF_COHORT, cohort_count=3)

    total = total_resource_pools([first, second])

    assert total.structural_carbon_kg == 2.0
    assert total.reserve_carbon_kg == 0.2
    assert total.water_kg == 4.0
    assert total.nitrogen_kg == 0.02
    assert total.phosphorus_kg == 0.002
    assert total.potassium_kg == 0.004
