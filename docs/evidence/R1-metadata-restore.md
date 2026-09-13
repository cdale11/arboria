# R1 Metadata Restore Evidence

## Scope

- Added checkpoint loading and validation for metadata-only `manifest.json` and `state.json` generations.
- Added CSRF-protected `POST /api/v1/saves/restore` accepting either `checkpoint_id` or named save `name`.
- Restore validates checkpoint identity, file size, and SHA-256 hash before changing live metadata.
- Restore applies saved clock and tick/revision state, sets the active checkpoint ID, and rotates timeline/request epoch.

## Evidence

- `python -m pytest tests/unit/app/test_checkpoints.py tests/unit/app/test_metadata.py tests/unit/app/test_server.py` passed with 38 tests and the documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check src/arboria/app/checkpoints.py src/arboria/app/metadata.py src/arboria/app/server.py tests/unit/app/test_checkpoints.py tests/unit/app/test_metadata.py tests/unit/app/test_server.py` passed.
- `mypy src tests/unit` passed.

## Limitations

- Restore currently applies metadata-only checkpoints.
- Biology, economy, learner state, RNG streams, pending events, pre-restore safety snapshots, export/import, autosave, retention, UI, and full corruption-recovery flows remain unimplemented.
