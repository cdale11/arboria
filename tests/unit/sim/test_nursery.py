import pytest

from arboria.sim.nursery import (
    STARTER_RESERVOIR_KG,
    advance_nursery,
    organs_from_payload,
    organs_to_payload,
    project_plants,
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

    summary = summarize(organs, zones, reservoir_kg=STARTER_RESERVOIR_KG)

    assert summary.plant_count == 2
    assert summary.organ_count == 6
    assert len(project_plants(organs, zones)) == 2


def test_nursery_tick_increases_carbon_and_stem_length() -> None:
    before = starter_organs()
    zones = starter_zones()
    before_summary = summarize(before, zones)
    before_stem = next(organ for organ in before if organ.organ_id == 2).length_m

    result = advance_nursery(before, zones, 2)

    assert result.uptake_kg > 0.0
    assert result.transpired_kg >= 0.0
    after_summary = summarize(
        result.organs, result.zones, uptake_kg=result.uptake_kg
    )
    assert after_summary.reserve_carbon_kg > before_summary.reserve_carbon_kg
    assert (
        after_summary.structural_carbon_kg >= before_summary.structural_carbon_kg
    )
    stem = next(organ for organ in result.organs if organ.organ_id == 2)
    assert stem.length_m > before_stem


def test_nursery_payload_round_trip_preserves_topology() -> None:
    organs = starter_organs()
    zones = starter_zones()

    restored = organs_from_payload(organs_to_payload(organs))
    restored_zones = zones_from_payload(zones_to_payload(zones), restored)

    assert len(restored) == len(organs)
    assert summarize(restored, restored_zones).plant_count == 2


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
