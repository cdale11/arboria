"""Single-writer world tick accumulator for the current R1 baseline."""

from __future__ import annotations

from dataclasses import dataclass

from arboria.sim.clock import BASE_TICK_SECONDS, ClockState

MAX_TICKS_PER_DRAIN = 100


@dataclass(frozen=True)
class WorldLoopState:
    sim_tick: int
    world_revision: int
    consumed_sim_time_seconds: float


class WorldLoop:
    """Consume elapsed simulation time into fixed biological tick boundaries."""

    def __init__(self, state: WorldLoopState | None = None) -> None:
        self._state = state or WorldLoopState(0, 0, 0.0)

    def state(self) -> WorldLoopState:
        return self._state

    def drain(self, clock: ClockState) -> WorldLoopState:
        if clock.paused or clock.sim_time_seconds < self._state.consumed_sim_time_seconds:
            return self._state
        available = clock.sim_time_seconds - self._state.consumed_sim_time_seconds
        ticks = min(int(available // BASE_TICK_SECONDS), MAX_TICKS_PER_DRAIN)
        if ticks <= 0:
            return self._state
        self._state = WorldLoopState(
            sim_tick=self._state.sim_tick + ticks,
            world_revision=self._state.world_revision + ticks,
            consumed_sim_time_seconds=self._state.consumed_sim_time_seconds
            + ticks * BASE_TICK_SECONDS,
        )
        return self._state
