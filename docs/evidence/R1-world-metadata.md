# R1 World Metadata Evidence

## Scope

- Added a SQLite metadata store at `world.sqlite3` under `ARBORIA_DATA_DIR`.
- Persisted one authenticated single-world identity, a fresh process-start timeline identity, schema version, and simulation clock state.
- Restart now keeps the world UUID, rotates the timeline UUID, and resumes the saved clock state without wall-clock catch-up.
- Exposed authenticated `/api/v1/world` metadata status.

## Evidence

- `python -m pytest tests/unit/app/test_metadata.py tests/unit/app/test_server.py tests/unit/sim/test_clock.py` passed with 20 tests and the documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check src/arboria/app/metadata.py src/arboria/app/server.py src/arboria/sim/clock.py tests/unit/app/test_metadata.py tests/unit/app/test_server.py tests/unit/sim/test_clock.py` passed.
- `mypy src tests/unit` passed.

## Limitations

- This is metadata persistence only, not complete save/restore.
- Immutable checkpoint generations, autosave, named saves, restore, export/import, command receipts, migrations, and biological world state are still unimplemented.
- Clock state is saved on clock requests, clock mutations, and graceful server shutdown; full tick-boundary checkpoint durability is a later R1 item.
