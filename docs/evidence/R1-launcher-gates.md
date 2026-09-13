# R1 launcher gates — evidence

Date: 2026-09-14.

## Scope

- `run.sh` supports `ARBORIA_LAUNCHER_CHECK=1`, which runs Conda activation,
  npm dependency availability, shared-password setup, frontend fingerprint
  comparison/rebuild, and then exits without starting Uvicorn.
- Unit tests exercise invalid port rejection, arbitrary working directory,
  path-with-spaces launch roots, stale fingerprint rebuild, and repeat check
  without unnecessary rebuild.
- The launcher continues to prioritize Conda Node/npm through
  `PATH="$CONDA_PREFIX/bin:$PATH"` before npm commands.

## Commands Run

```bash
python -m pytest tests/unit/app/test_shop_api.py tests/unit/app/test_launcher.py
PATH="$CONDA_PREFIX/bin:$PATH" npm --prefix web run test
PATH="$CONDA_PREFIX/bin:$PATH" npm --prefix web run test:e2e
```

## Results

- `python -m pytest tests/unit/app/test_shop_api.py tests/unit/app/test_launcher.py`
  passed with 15 tests and the known FastAPI/Starlette `TestClient` deprecation
  warning.
- `npm --prefix web run test` passed with 18 tests.
- `npm --prefix web run test:e2e` passed with one full-flow jsdom test.

## Limitations

- The repeat-start check is local/cache-based. It does not forcibly disable all
  network interfaces; no package install occurs when dependencies are already
  present.
- Interrupted build recovery is represented by stale fingerprint detection and
  rebuild, not by killing a build subprocess mid-write.
- Signal forwarding and graceful shutdown save remain covered by lifecycle
  tests and evidence, not by this check-mode test file.
