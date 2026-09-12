# R1 simulation-clock baseline evidence

Date: 2026-09-13. Scope: authenticated in-memory simulation clock with default 48x speed, pause/resume, speed control, and status reporting. This is not evidence that biological ticks, persistence, offline resume, economy, companion, or world simulation exists.

## Implemented scope

- `SimulationClock` advances simulated seconds from monotonic runtime at default speed 48x.
- Clock status reports simulated seconds, speed, pause state, base tick seconds, day index, day of year, and year.
- Pause stops simulated time advancement until resume.
- Speed updates validate the configured 1x to 144x normal range.
- `/api/v1/clock` requires authentication.
- `/api/v1/clock/pause`, `/api/v1/clock/resume`, and `/api/v1/clock/speed` require authentication and CSRF.
- Health reports `simulation_clock: true` while full `simulation` remains false.

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
python health probe against http://127.0.0.1:8767/health
```

## Results

- `python -m pytest tests/unit` passed with 17 tests and the previously documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed.
- `npm --prefix web run build` passed.
- `./run.sh` served `/health` with phase `r1-clock-baseline` and `simulation_clock: true`.

## Limitations

- Clock state is in memory only; restart currently resets it because checkpoint persistence is not implemented.
- No biological tick loop consumes the clock yet.
- No command queue or frontend clock controls exist yet; the current API is direct server baseline behavior.
