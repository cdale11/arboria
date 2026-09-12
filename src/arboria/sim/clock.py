"""Server-owned simulation clock for the current R1 baseline."""

from __future__ import annotations

import time
from dataclasses import dataclass

DEFAULT_SPEED = 48.0
MIN_SPEED = 1.0
MAX_SPEED = 144.0
BASE_TICK_SECONDS = 300
SECONDS_PER_DAY = 86_400
DAYS_PER_YEAR = 365


class ClockValidationError(ValueError):
    """Raised when a clock command violates the configured contract."""


@dataclass(frozen=True)
class ClockStatus:
    sim_time_seconds: float
    speed: float
    paused: bool
    base_tick_seconds: int
    day_index: int
    day_of_year: int
    year: int


@dataclass(frozen=True)
class ClockState:
    sim_time_seconds: float
    speed: float
    paused: bool


class SimulationClock:
    """Convert monotonic server runtime into deterministic simulated time."""

    def __init__(
        self,
        *,
        now: float | None = None,
        speed: float = DEFAULT_SPEED,
        sim_time_seconds: float = 0.0,
        paused: bool = False,
    ) -> None:
        if sim_time_seconds < 0.0:
            raise ClockValidationError("Simulation time cannot be negative.")
        self._sim_time_seconds = float(sim_time_seconds)
        self._speed = self._validate_speed(speed)
        self._paused = paused
        self._last_monotonic = self._now(now)

    @classmethod
    def from_state(cls, state: ClockState, *, now: float | None = None) -> SimulationClock:
        return cls(
            now=now,
            speed=state.speed,
            sim_time_seconds=state.sim_time_seconds,
            paused=state.paused,
        )

    def state(self, *, now: float | None = None) -> ClockState:
        self._advance(now)
        return ClockState(
            sim_time_seconds=self._sim_time_seconds,
            speed=self._speed,
            paused=self._paused,
        )

    def status(self, *, now: float | None = None) -> ClockStatus:
        self._advance(now)
        day_index = int(self._sim_time_seconds // SECONDS_PER_DAY)
        return ClockStatus(
            sim_time_seconds=self._sim_time_seconds,
            speed=self._speed,
            paused=self._paused,
            base_tick_seconds=BASE_TICK_SECONDS,
            day_index=day_index,
            day_of_year=day_index % DAYS_PER_YEAR,
            year=day_index // DAYS_PER_YEAR,
        )

    def pause(self, *, now: float | None = None) -> ClockStatus:
        self._advance(now)
        self._paused = True
        return self.status(now=now)

    def resume(self, *, now: float | None = None) -> ClockStatus:
        self._last_monotonic = self._now(now)
        self._paused = False
        return self.status(now=now)

    def set_speed(self, speed: float, *, now: float | None = None) -> ClockStatus:
        self._advance(now)
        self._speed = self._validate_speed(speed)
        self._last_monotonic = self._now(now)
        return self.status(now=now)

    def _advance(self, now: float | None = None) -> None:
        current = self._now(now)
        elapsed = max(0.0, current - self._last_monotonic)
        if not self._paused:
            self._sim_time_seconds += elapsed * self._speed
        self._last_monotonic = current

    @staticmethod
    def _now(now: float | None = None) -> float:
        return time.monotonic() if now is None else now

    @staticmethod
    def _validate_speed(speed: float) -> float:
        if not (MIN_SPEED <= speed <= MAX_SPEED):
            raise ClockValidationError(
                f"Simulation speed must be between {MIN_SPEED:g}x and {MAX_SPEED:g}x."
            )
        return float(speed)


def clock_status_payload(status: ClockStatus) -> dict[str, float | int | bool]:
    return {
        "sim_time_seconds": status.sim_time_seconds,
        "speed": status.speed,
        "paused": status.paused,
        "base_tick_seconds": status.base_tick_seconds,
        "day_index": status.day_index,
        "day_of_year": status.day_of_year,
        "year": status.year,
    }
