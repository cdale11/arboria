# R1 Active Checkpoint Validation Evidence

## Scope

- Added startup validation for the recorded active metadata checkpoint.
- Startup validates checkpoint file presence, manifest checkpoint ID, `state.json` size, and SHA-256 hash before the app admits clients.
- Corrupt active metadata checkpoints are no longer fatal: validation still
  rejects the damaged generation, but startup now recovers through the
  parent-chain fallback in `docs/evidence/R1-recovery.md` instead of failing.

## Evidence

- `python -m pytest tests/unit/app/test_checkpoints.py tests/unit/app/test_server.py` passed with 36 tests and the documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check src/arboria/app/server.py tests/unit/app/test_server.py` passed.
- `mypy src tests/unit` passed.

## Limitations

- This validates metadata-only active checkpoints.
- Fallback selection, repair policy, import validation, disk-full handling, migrations, and complete biology/economy/learner recovery were open at the time; fallback, migration, and failure-injection evidence now lives in `docs/evidence/R1-recovery.md`.
