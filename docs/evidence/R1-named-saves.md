# R1 Named Saves Evidence

## Scope

- Added SQLite `snapshot_names` records for metadata-only named saves.
- Added authenticated `GET /api/v1/saves` to list named snapshots.
- Added CSRF-protected `POST /api/v1/saves/named` to create a metadata-only checkpoint and attach a protected user-visible name.
- Validated names are nonempty, bounded to 80 characters, and cannot contain path separators.

## Evidence

- `python -m pytest tests/unit/app/test_metadata.py tests/unit/app/test_server.py` passed with 34 tests and the documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check src/arboria/app/metadata.py src/arboria/app/server.py tests/unit/app/test_metadata.py tests/unit/app/test_server.py` passed.
- `mypy src tests/unit` passed.

## Limitations

- Named saves currently point to metadata-only checkpoints.
- Restore, export/import, autosave, retention, corruption recovery, biology/economy/learner checkpoint contents, and save UI are still unimplemented.
