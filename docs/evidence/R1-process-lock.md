# R1 process-lock baseline evidence

Date: 2026-09-13. Scope: OS-backed data-directory process lock integrated with the current FastAPI server lifecycle. This is not evidence that biological simulation, save/checkpoint persistence, migrations, crash recovery, economy, companion, or command streaming exists.

## Implemented scope

- `DataDirectoryLock` acquires a nonblocking exclusive `flock` on `server.lock` under `ARBORIA_DATA_DIR`.
- The lock file records the owning PID for diagnostics and is permissioned owner-read/write.
- The server acquires the lock on FastAPI lifespan startup and releases it on shutdown.
- A second owner using the same data directory receives `ProcessLockError` instead of sharing mutable ownership.
- Health reports `process_lock: true` in the implemented status map.

## Commands run

```bash
python -m pytest tests/unit
ruff check .
mypy src tests/unit
PATH="$CONDA_PREFIX/bin:$PATH" npm --prefix web run check
PATH="$CONDA_PREFIX/bin:$PATH" npm --prefix web run test
PATH="$CONDA_PREFIX/bin:$PATH" npm --prefix web run build
ARBORIA_HOST=127.0.0.1 ARBORIA_PORT=8767 ARBORIA_DATA_DIR=<tmp> \
  ARBORIA_SETUP_PASSWORD=<temporary> ./run.sh
second run with same ARBORIA_DATA_DIR on port 8768, expected startup failure
```

## Results

- `python -m pytest tests/unit` passed with 10 tests and the previously documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed.
- `npm --prefix web run build` passed.
- A first `./run.sh` process served `/health` from an isolated data directory.
- A second `./run.sh` process using the same data directory failed during startup instead of serving concurrently.
- After terminating the first process, the data-directory lock became acquirable again in unit coverage.

## Limitations

- This is an advisory local-process lock on the supported local filesystem, not a network-filesystem or distributed lock guarantee.
- No SQLite database, checkpoint generation, autosave, migration, or restore machinery exists yet.
- Auth setup still occurs before server lifespan lock acquisition; no mutable world data exists at that point. Future world/database initialization must happen under the lock.
