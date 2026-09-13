# R1 Interrupted Checkpoint Cleanup Evidence

## Scope

- Added startup cleanup for interrupted metadata-checkpoint generation directories.
- Cleanup removes only hidden directories under `checkpoints/` whose names start with `.` and end with `.tmp`.
- Complete checkpoint directories are left untouched.

## Evidence

- `python -m pytest tests/unit/app/test_checkpoints.py tests/unit/app/test_server.py` passed with 35 tests and the documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check src/arboria/app/checkpoints.py src/arboria/app/server.py tests/unit/app/test_checkpoints.py tests/unit/app/test_server.py` passed.
- `mypy src tests/unit` passed.

## Limitations

- This only handles interrupted pre-registration checkpoint generation directories.
- Active-checkpoint corruption handling, disk-full behavior, migration tooling, restore fallback selection, retention, and failure-injection tests remain unimplemented.
