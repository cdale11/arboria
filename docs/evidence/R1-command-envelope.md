# R1 Command Envelope Evidence

## Scope

- Added bounded command envelope validation for `schema_version`, UUID identity fields, request epoch, command kind, and JSON payload structure.
- Added persisted command receipts in `world.sqlite3`, keyed by active timeline, request epoch, and command ID.
- Added request epoch metadata that increments on process restart alongside the existing timeline rotation.
- Added authenticated, CSRF-protected `POST /api/v1/commands`.
- Routed existing real clock actions through the command path for `clock.pause`, `clock.resume`, and `clock.set_speed`.

## Evidence

- `python -m pytest tests/unit/app/test_commands.py tests/unit/app/test_metadata.py tests/unit/app/test_server.py` passed with 22 tests and the documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check src/arboria/app/commands.py src/arboria/app/metadata.py src/arboria/app/server.py tests/unit/app/test_commands.py tests/unit/app/test_metadata.py tests/unit/app/test_server.py` passed.
- `mypy src tests/unit` passed.

## Limitations

- No horticultural command kinds exist yet.
- Clock commands are applied immediately because lifecycle controls must remain serviceable while paused; the one-writer biological tick loop is still unimplemented.
- Receipt retention/expiry policy, queue capacity controls, checkpoint reconciliation, and WebSocket execution notifications remain later R1 items.
