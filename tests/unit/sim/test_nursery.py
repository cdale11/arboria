import pytest

from arboria.biology.nutrients import NutrientZone
from arboria.sim.nursery import (
    NURSERY_SCHEMA_VERSION,
    STARTER_RESERVOIR_KG,
    add_starter_plant,
    advance_nursery,
    load_nursery_state,
    nutrient_zones_from_payload,
    nutrient_zones_to_payload,
    organs_from_payload,
    organs_to_payload,
    project_plants,
    remove_plant,
    species_from_payload,
    species_to_payload,
    starter_nutrient_zones,
    starter_organs,
    starter_plant_organs,
    starter_species_by_plant,
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


def test_add_starter_plant_grows_inventory_with_fresh_ids() -> None:
    organs = starter_organs()
    mapping = starter_species_by_plant()

    next_organs, next_zones, next_nutrients, next_mapping, plant_id = add_starter_plant(
        organs, starter_zones(), starter_nutrient_zones(), mapping, "crassula_ovata"
    )

    assert plant_id == 3
    assert len(next_organs) == len(organs) + 3
    assert next_mapping[3] == "crassula_ovata"
    projections = project_plants(next_organs, next_zones, next_nutrients, next_mapping)
    assert [item.plant_id for item in projections] == [1, 2, 3]
    assert summarize(
        next_organs, next_zones, next_nutrients, species_by_plant=next_mapping
    ).plant_count == 3
    with pytest.raises(ValueError, match="unknown species"):
        add_starter_plant(organs, starter_zones(), starter_nutrient_zones(), mapping, "moss")


def test_remove_plant_drops_topology_zones_and_mapping() -> None:
    organs = starter_organs()
    mapping = starter_species_by_plant()
    grown, zones, nutrients, grown_mapping, _ = add_starter_plant(
        organs, starter_zones(), starter_nutrient_zones(), mapping, "crassula_ovata"
    )

    next_organs, next_zones, next_nutrients, next_mapping, species_id = remove_plant(
        grown, zones, nutrients, grown_mapping, 3
    )

    assert species_id == "crassula_ovata"
    assert [organ.plant_id for organ in next_organs] == [1, 1, 1, 2, 2, 2]
    assert sorted(next_zones) == [1, 2]
    assert sorted(next_mapping) == [1, 2]
    with pytest.raises(ValueError, match="unknown plant"):
        remove_plant(next_organs, next_zones, next_nutrients, next_mapping, 3)


def test_bought_plants_tick_with_their_species() -> None:
    organs = starter_organs()
    mapping = starter_species_by_plant()
    grown, zones, nutrients, grown_mapping, _ = add_starter_plant(
        organs, starter_zones(), starter_nutrient_zones(), mapping, "crassula_ovata"
    )

    result = advance_nursery(grown, zones, nutrients, 5, grown_mapping)

    projections = project_plants(
        result.organs, result.zones, result.nutrient_zones, grown_mapping
    )
    assert [item.species_id for item in projections] == [
        "ocimum_basilicum",
        "quercus_robur",
        "crassula_ovata",
    ]
    assert all(item.alive for item in projections)


def test_species_payload_round_trip_and_starter_fallback() -> None:
    organs = starter_organs()
    mapping = starter_species_by_plant()

    restored = species_from_payload(species_to_payload(mapping), organs)

    assert restored == mapping
    assert species_from_payload([], organs) == mapping
    with pytest.raises(ValueError, match="exactly once"):
        species_from_payload([{"plant_id": 1, "species_id": "ocimum_basilicum"}], organs)
    unmapped = starter_plant_organs(9, "crassula_ovata", 1)
    with pytest.raises(ValueError, match="no species assigned"):
        species_from_payload([], unmapped)


def test_versioned_migration_loads_old_checkpoint_states() -> None:
    organs = starter_organs()
    organ_payload = organs_to_payload(organs)
    restored_organs = organs_from_payload(organ_payload)

    oldest = load_nursery_state(
        {"nursery_schema_version": 1, "nursery_organs": organ_payload}, restored_organs
    )
    assert oldest.zones == starter_zones()
    assert oldest.nutrient_zones == starter_nutrient_zones()
    assert oldest.species_by_plant == starter_species_by_plant()

    custom_zones = zones_to_payload({1: 0.05, 2: 0.06})
    migrated = load_nursery_state(
        {
            "nursery_schema_version": 2,
            "nursery_organs": organ_payload,
            "nursery_zones": custom_zones,
        },
        restored_organs,
    )
    assert migrated.zones == {1: 0.05, 2: 0.06}
    assert migrated.nutrient_zones == starter_nutrient_zones()

    full = load_nursery_state(
        {
            "nursery_schema_version": NURSERY_SCHEMA_VERSION,
            "nursery_organs": organ_payload,
            "nursery_zones": custom_zones,
            "nursery_nutrient_zones": nutrient_zones_to_payload(
                starter_nutrient_zones()
            ),
            "nursery_species": species_to_payload(starter_species_by_plant()),
        },
        restored_organs,
    )
    assert full.zones == {1: 0.05, 2: 0.06}
    assert full.species_by_plant == starter_species_by_plant()


def test_versioned_migration_rejects_newer_and_invalid_versions() -> None:
    organs = starter_organs()
    organ_payload = organs_to_payload(organs)
    restored_organs = organs_from_payload(organ_payload)

    for bad_version in (0, -1, NURSERY_SCHEMA_VERSION + 1, "4", True, None):
        with pytest.raises(ValueError, match="[Vv]ersion"):
            load_nursery_state(
                {"nursery_schema_version": bad_version, "nursery_organs": organ_payload},
                restored_organs,
            )
