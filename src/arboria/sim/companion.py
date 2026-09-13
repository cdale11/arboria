"""Deterministic R1 caretaker policy over authoritative nursery projections.

This is the baseline caretaker required before learned management. It proposes
only existing, bounded commands; the application must submit each proposal
through the ordinary command validator before mutation.
"""

from __future__ import annotations

from dataclasses import dataclass

from .nursery import PlantProjection

COMPANION_SCHEMA_VERSION = 1
DEFAULT_WATER_THRESHOLD = 0.55
DEFAULT_WATER_AMOUNT_KG = 0.05


@dataclass(frozen=True)
class CompanionPolicy:
    """Persisted caretaker policy and hard action budget."""

    enabled: bool = False
    water_threshold: float = DEFAULT_WATER_THRESHOLD
    max_actions_per_tick: int = 1


@dataclass(frozen=True)
class CompanionState:
    """Persisted caretaker counters and most recent decision explanation."""

    policy: CompanionPolicy = CompanionPolicy()
    actions_proposed: int = 0
    actions_applied: int = 0
    actions_rejected: int = 0
    last_reason: str | None = None
    last_plant_id: int | None = None


@dataclass(frozen=True)
class CompanionAction:
    kind: str
    payload: dict[str, float | int]
    plant_id: int
    reason: str


def validate_policy(policy: CompanionPolicy) -> None:
    if not isinstance(policy.enabled, bool):
        raise ValueError("companion enabled must be a boolean")
    if not 0.0 <= policy.water_threshold <= 1.0:
        raise ValueError("companion water threshold must be between 0 and 1")
    if policy.max_actions_per_tick < 0 or policy.max_actions_per_tick > 4:
        raise ValueError("companion action budget must be between 0 and 4")


def choose_actions(
    plants: list[PlantProjection],
    *,
    policy: CompanionPolicy,
    reservoir_kg: float,
    protected_plant_ids: set[int],
) -> list[CompanionAction]:
    """Choose bounded watering actions, prioritizing the most stressed plant."""
    validate_policy(policy)
    if not policy.enabled or policy.max_actions_per_tick == 0 or reservoir_kg <= 0.0:
        return []
    candidates = [
        plant
        for plant in plants
        if plant.alive
        and plant.water_stress_factor < policy.water_threshold
    ]
    candidates.sort(key=lambda plant: (plant.water_stress_factor, plant.plant_id))
    actions: list[CompanionAction] = []
    for plant in candidates[: policy.max_actions_per_tick]:
        actions.append(
            CompanionAction(
                kind="nursery.water",
                payload={"plant_id": plant.plant_id, "water_kg": DEFAULT_WATER_AMOUNT_KG},
                plant_id=plant.plant_id,
                reason=(
                    f"water plant {plant.plant_id}: water stress "
                    f"{plant.water_stress_factor:.2f} below threshold "
                    f"{policy.water_threshold:.2f}"
                ),
            )
        )
    return actions
