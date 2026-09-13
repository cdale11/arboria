# R1 World Loop Evidence

## Scope

- Added a single in-process `WorldLoop` accumulator that consumes clock state into fixed 300-sim-second ticks.
- Added persisted `sim_tick`, `world_revision`, and consumed simulation time fields in `world.sqlite3`.
- Exposed tick/revision fields through authenticated `/api/v1/world` and stream snapshots.
- Bounded each drain to at most 100 ticks to avoid unbounded request-time catch-up work.

## Evidence

- `python -m pytest tests/unit/sim/test_world_loop.py tests/unit/app/test_metadata.py tests/unit/app/test_server.py` passed with 28 tests and the documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check src/arboria/sim/world_loop.py src/arboria/app/metadata.py src/arboria/app/server.py tests/unit/sim/test_world_loop.py tests/unit/app/test_metadata.py tests/unit/app/test_server.py` passed.
- `mypy src tests/unit` passed.

## Limitations

- No biological kernels, event processing, manager planning, horticultural commands, projection deltas, or checkpoint scheduling run on ticks yet.
- The loop drains when server code observes clock/world state; a dedicated background owner loop and shutdown orchestration remain later R1 work.
