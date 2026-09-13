# R1 Metadata Autosave Evidence

## Scope

- Added metadata-only autosave checkpoint purpose and persisted last autosave timestamp.
- Added `purpose` to checkpoint manifests, checkpoint state, and SQLite checkpoint records.
- Added autosave status fields to `GET /api/v1/saves`.
- Triggered due autosaves from authenticated world status checks.
- Kept the default autosave interval at 60 seconds; tests may set `ARBORIA_AUTOSAVE_INTERVAL_SECONDS=0` for deterministic autosave.

## Evidence

- `python -m pytest tests/unit/app/test_checkpoints.py tests/unit/app/test_metadata.py tests/unit/app/test_server.py` passed with 41 tests and the documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check src/arboria/app/checkpoints.py src/arboria/app/metadata.py src/arboria/app/server.py tests/unit/app/test_checkpoints.py tests/unit/app/test_metadata.py tests/unit/app/test_server.py` passed.
- `mypy src tests/unit` passed.

## Limitations

- Autosave currently captures metadata-only checkpoints.
- There is no background autosave worker, restore safety snapshot, retention policy, export/import, biology/economy/learner state, or UI yet.
