# R1 Active Checkpoint Validation Evidence

## Scope

- Added startup validation for the recorded active metadata checkpoint.
- Startup validates checkpoint file presence, manifest checkpoint ID, `state.json` size, and SHA-256 hash before the app admits clients.
- Corrupt active metadata checkpoints fail startup clearly instead of being silently ignored.

## Evidence

- `python -m pytest tests/unit/app/test_checkpoints.py tests/unit/app/test_server.py` passed with 36 tests and the documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check src/arboria/app/server.py tests/unit/app/test_server.py` passed.
- `mypy src tests/unit` passed.

## Limitations

- This validates metadata-only active checkpoints.
- It does not yet offer fallback selection, repair, import validation, disk-full handling, migrations, or complete biology/economy/learner recovery.
