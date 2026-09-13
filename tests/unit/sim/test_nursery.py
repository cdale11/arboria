import pytest

from arboria.biology.nutrients import NutrientZone
from arboria.sim.nursery import (
    STARTER_RESERVOIR_KG,
    advance_nursery,
    nutrient_zones_from_payload,
    nutrient_zones_to_payload,
    organs_from_payload,
    organs_to_payload,
    project_plants,
    starter_nutrient_zones,
    starter_organs,
    starter_zones,
    summarize,
    water_plant,
    zones_from_payload,
    zones_to_payload,
)


def test_starter_nursery_has_two_plants() -> None:
    organs = starter_organs()
    zones = starter_zones()
    nutrients = starter_nutrient_zones()

    summary = summarize(organs, zones, nutrients, reservoir_kg=STARTER_RESERVOIR_KG)

    assert summary.plant_count == 2
    assert summary.organ_count == 6
    assert summary.dead_plant_count == 0
    projections = project_plants(organs, zones, nutrients)
    assert len(projections) == 2
    assert all(projection.alive for projection in projections)
    assert all(
        projection.nutrient_stress_factor == pytest.approx(1.0)
        for projection in projections
    )


def test_nursery_tick_increases_carbon_and_stem_length() -> None:
    before = starter_organs()
    zones = starter_zones()
    nutrients = starter_nutrient_zones()
    before_summary = summarize(before, zones, nutrients)
    before_stem = next(organ for organ in before if organ.organ_id == 2).length_m

    result = advance_nursery(before, zones, nutrients, 2)

    assert result.uptake_kg > 0.0
    assert result.transpired_kg >= 0.0
    assert sum(result.npk_uptake_kg) > 0.0
    after_summary = summarize(
        result.organs, result.zones, result.nutrient_zones, uptake_kg=result.uptake_kg
    )
    assert after_summary.reserve_carbon_kg > before_summary.reserve_carbon_kg
    assert (
        after_summary.structural_carbon_kg >= before_summary.structural_carbon_kg
    )
    stem = next(organ for organ in result.organs if organ.organ_id == 2)
    assert stem.length_m > before_stem


def test_nutrient_zones_deplete_without_fertilizer_input() -> None:
    result = advance_nursery(
        starter_organs(), starter_zones(), starter_nutrient_zones(), 50
    )

    assert result.nutrient_zones[1].nitrogen_kg < 0.020
    assert result.nutrient_zones[1].phosphorus_kg < 0.0040
    assert result.nutrient_zones[1].potassium_kg < 0.0080


def test_prolonged_starvation_kills_plants_which_stop_ticking() -> None:
    starved = {
        plant_id: NutrientZone(
            nitrogen_kg=0.0, phosphorus_kg=0.0, potassium_kg=0.0
        )
        for plant_id in (1, 2)
    }
    result = advance_nursery(starter_organs(), starter_zones(), starved, 20000)

    summary = summarize(result.organs, result.zones, result.nutrient_zones)
    assert summary.dead_plant_count == 2
    projections = project_plants(result.organs, result.zones, result.nutrient_zones)
    assert all(not projection.alive for projection in projections)
    roots = [organ for organ in result.organs if organ.parent_id is None]
    assert all(not root.alive and root.damage_fraction == 1.0 for root in roots)

    continued = advance_nursery(
        result.organs, result.zones, result.nutrient_zones, 10
    )
    assert [organ.length_m for organ in continued.organs] == [
        organ.length_m for organ in result.organs
    ]


def test_nursery_payload_round_trip_preserves_topology() -> None:
    organs = starter_organs()
    zones = starter_zones()
    nutrients = starter_nutrient_zones()

    restored = organs_from_payload(organs_to_payload(organs))
    restored_zones = zones_from_payload(zones_to_payload(zones), restored)
    restored_nutrients = nutrient_zones_from_payload(
        nutrient_zones_to_payload(nutrients), restored
    )

    assert len(restored) == len(organs)
    assert summarize(restored, restored_zones, restored_nutrients).plant_count == 2


def test_nutrient_payload_falls_back_to_starter_values() -> None:
    organs = starter_organs()

    restored = nutrient_zones_from_payload([], organs)

    assert restored[1].nitrogen_kg == pytest.approx(0.020)


def test_watering_moves_reservoir_to_zone_with_conservation() -> None:
    zones = starter_zones()

    next_zones, reservoir_after, drainage = water_plant(
        zones, STARTER_RESERVOIR_KG, 1, 0.05
    )

    assert next_zones[1] == pytest.approx(zones[1] + 0.05 - drainage)
    assert reservoir_after == pytest.approx(STARTER_RESERVOIR_KG - 0.05)


def test_watering_rejects_unknown_plant_and_over_limit() -> None:
    with pytest.raises(ValueError, match="unknown plant"):
        water_plant(starter_zones(), STARTER_RESERVOIR_KG, 999, 0.01)
    with pytest.raises(ValueError, match="per-command limit"):
        water_plant(starter_zones(), STARTER_RESERVOIR_KG, 1, 1.0)
