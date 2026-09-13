import pytest

from arboria.sim.companion import CompanionPolicy, choose_actions, validate_policy
from arboria.sim.nursery import (
    project_plants,
    starter_nutrient_zones,
    starter_organs,
    starter_zones,
)


def test_caretaker_prioritizes_low_water_plant() -> None:
    plants = project_plants(starter_organs(), starter_zones(), starter_nutrient_zones())
    policy = CompanionPolicy(enabled=True, water_threshold=0.8, max_actions_per_tick=1)

    actions = choose_actions(
        plants,
        policy=policy,
        reservoir_kg=2.0,
        protected_plant_ids=set(),
    )

    assert len(actions) == 1
    assert actions[0].kind == "nursery.water"
    assert actions[0].plant_id == 1


def test_caretaker_is_bounded_and_does_not_sell() -> None:
    plants = project_plants(starter_organs(), starter_zones(), starter_nutrient_zones())
    policy = CompanionPolicy(enabled=True, water_threshold=1.0, max_actions_per_tick=1)

    actions = choose_actions(
        plants,
        policy=policy,
        reservoir_kg=0.0,
        protected_plant_ids={1, 2},
    )

    assert actions == []
    assert all(action.kind == "nursery.water" for action in actions)


def test_policy_rejects_unbounded_action_budget() -> None:
    with pytest.raises(ValueError, match="action budget"):
        validate_policy(CompanionPolicy(max_actions_per_tick=5))
