from arboria.sim.nursery import (
    advance_nursery,
    organs_from_payload,
    organs_to_payload,
    project_plants,
    starter_organs,
    summarize,
)


def test_starter_nursery_has_two_plants() -> None:
    organs = starter_organs()

    summary = summarize(organs)

    assert summary.plant_count == 2
    assert summary.organ_count == 6
    assert len(project_plants(organs)) == 2


def test_nursery_tick_increases_carbon_and_stem_length() -> None:
    before = starter_organs()
    before_reserve = summarize(before).reserve_carbon_kg
    before_length = sum(
        organ.length_m for organ in before if organ.plant_id == 1 and organ.organ_id == 2
    )

    after, uptake = advance_nursery(before, 2)

    assert uptake > 0.0
    assert summarize(after).reserve_carbon_kg > before_reserve
    assert summarize(after).structural_carbon_kg >= summarize(before).structural_carbon_kg
    stem = next(organ for organ in after if organ.organ_id == 2)
    assert stem.length_m > before_length


def test_nursery_payload_round_trip_preserves_topology() -> None:
    organs = starter_organs()

    restored = organs_from_payload(organs_to_payload(organs))

    assert len(restored) == len(organs)
    assert summarize(restored).plant_count == 2
