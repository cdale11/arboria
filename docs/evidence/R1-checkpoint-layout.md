# R1 Checkpoint Layout Evidence

## Scope

- Added immutable checkpoint generation directories under `checkpoints/<checkpoint_id>/`.
- Added `manifest.json` with format version, world/timeline identity, checkpoint parent, clock/tick/revision state, request epoch, file size, and SHA-256 metadata.
- Added `state.json` capturing the current metadata-only authoritative state.
- Added SQLite `checkpoints` records and active checkpoint ID updates.
- Added authenticated, CSRF-protected `POST /api/v1/saves/checkpoint` for manual metadata-only checkpoints.

## Evidence

- `python -m pytest tests/unit/app/test_checkpoints.py tests/unit/app/test_metadata.py tests/unit/app/test_server.py` passed with 30 tests and the documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check src/arboria/app/checkpoints.py src/arboria/app/metadata.py src/arboria/app/server.py tests/unit/app/test_checkpoints.py tests/unit/app/test_metadata.py tests/unit/app/test_server.py` passed.
- `mypy src tests/unit` passed.

## Limitations

- Checkpoints currently contain metadata, clock, tick/revision state, and receipt count only.
- No biology, economy, learner state, pending events, autosave, named saves, restore, export/import, retention, corruption recovery, or failure-injection tests exist yet.
