# R1 launcher/server baseline evidence

Date: 2026-09-12. Scope: current `./run.sh`, static frontend build/serve baseline, FastAPI health endpoint, and smoke tests. This is not evidence that authentication, simulation, persistence, economy, companion behavior, or the final R1 playable loop exists.

## Implemented scope

- `run.sh` discovers Conda, activates `arboria`, forces `$CONDA_PREFIX/bin` ahead of inherited Node paths, validates `ARBORIA_PORT`, builds browser assets when a source/config fingerprint changes, and starts Uvicorn.
- `src/arboria/app/server.py` creates a FastAPI app with `/health` and `/api/v1/health` endpoints and static frontend serving when `web/dist` exists.
- The health payload explicitly reports implemented and unimplemented subsystems.
- Unit tests verify health endpoint scope and API/plain health consistency.

## Commands run

```bash
chmod +x run.sh
python -m pytest tests/unit
ruff check .
mypy src tests/unit
npm --prefix web run check
npm --prefix web run test
npm --prefix web run build
ARBORIA_PORT=8766 ./run.sh
python health probe against http://127.0.0.1:8766/health
```

## Expected current health payload shape

```json
{
  "status": "ok",
  "phase": "r1-launcher-baseline",
  "implemented": {
    "server": true,
    "static_frontend": true,
    "authentication": false,
    "simulation": false,
    "persistence": false,
    "companion": false
  }
}
```

## Results

- `python -m pytest tests/unit` passed with 2 tests. It emitted a `StarletteDeprecationWarning` from FastAPI's re-exported `TestClient`; this did not fail the suite.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed with 1 Vitest/jsdom smoke test.
- `npm --prefix web run build` passed.
- `ARBORIA_HOST=127.0.0.1 ARBORIA_PORT=8766 ./run.sh` served `/health` successfully and was terminated after the probe.

## Limitations

- Password setup and session authentication are not implemented.
- There is no world process, tick loop, simulation, save directory, migration, or process lock.
- `run.sh` installs browser dependencies only when `web/node_modules` is absent. Full fingerprinted dependency synchronization and interrupted-build recovery remain R1 launcher work.
- The smoke server was run on `127.0.0.1` through the default Uvicorn binding path supplied by `ARBORIA_HOST`; LAN/mobile validation was not performed.
- Offline repeat start was not separately verified in this slice.
