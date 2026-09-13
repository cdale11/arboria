from arboria.sim.clock import ClockState
from arboria.sim.world_loop import MAX_TICKS_PER_DRAIN, WorldLoop, WorldLoopState


def test_world_loop_consumes_300_second_tick_boundaries() -> None:
    loop = WorldLoop()

    state = loop.drain(ClockState(sim_time_seconds=650.0, speed=48.0, paused=False))

    assert state.sim_tick == 2
    assert state.world_revision == 2
    assert state.consumed_sim_time_seconds == 600.0


def test_world_loop_does_not_advance_while_paused() -> None:
    loop = WorldLoop(WorldLoopState(2, 2, 600.0))

    state = loop.drain(ClockState(sim_time_seconds=1200.0, speed=48.0, paused=True))

    assert state == WorldLoopState(2, 2, 600.0)


def test_world_loop_bounds_catchup_per_drain() -> None:
    loop = WorldLoop()

    state = loop.drain(ClockState(sim_time_seconds=100_000.0, speed=48.0, paused=False))

    assert state.sim_tick == MAX_TICKS_PER_DRAIN
    assert state.world_revision == MAX_TICKS_PER_DRAIN
