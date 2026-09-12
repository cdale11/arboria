import pytest

from arboria.sim.clock import DEFAULT_SPEED, ClockValidationError, SimulationClock


def test_clock_advances_at_default_speed() -> None:
    clock = SimulationClock(now=10.0)

    status = clock.status(now=20.0)

    assert status.sim_time_seconds == 10.0 * DEFAULT_SPEED
    assert status.day_index == 0
    assert status.day_of_year == 0
    assert status.year == 0


def test_clock_pause_blocks_time_until_resume() -> None:
    clock = SimulationClock(now=0.0)

    paused = clock.pause(now=5.0)
    later = clock.status(now=100.0)
    resumed = clock.resume(now=100.0)
    final = clock.status(now=105.0)

    assert paused.sim_time_seconds == 5.0 * DEFAULT_SPEED
    assert later.sim_time_seconds == paused.sim_time_seconds
    assert resumed.paused is False
    assert final.sim_time_seconds == paused.sim_time_seconds + 5.0 * DEFAULT_SPEED


def test_clock_speed_change_keeps_elapsed_time_before_change() -> None:
    clock = SimulationClock(now=0.0)

    changed = clock.set_speed(12.0, now=10.0)
    later = clock.status(now=20.0)

    assert changed.sim_time_seconds == 10.0 * DEFAULT_SPEED
    assert later.sim_time_seconds == changed.sim_time_seconds + 120.0


def test_clock_rejects_invalid_speed() -> None:
    with pytest.raises(ClockValidationError):
        SimulationClock(speed=0.0)

    clock = SimulationClock(now=0.0)
    with pytest.raises(ClockValidationError):
        clock.set_speed(145.0, now=1.0)
