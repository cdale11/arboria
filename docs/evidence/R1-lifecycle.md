# R1 lifecycle controls while paused — evidence

## Scope

No application code changed: pause, save, restore, resume, speed, shop, and
watering paths already stay serviceable while the simulation clock is paused.
This slice locks that behavior with sequence tests and a live shutdown run.

## Verification

- `python -m pytest tests/unit` passed with 131 tests, including
  `tests/unit/app/test_lifecycle.py`:
  - Pause freezes `sim_tick` across world reads while `nursery.water` and
    `shop.buy_water` still apply against the frozen tick with exact
    reservoir/cash accounting.
  - Checkpoint, named save, buy-plant, restore-by-name, speed change, and
    resume all succeed while paused; restore drops the bought plant, keeps
    the frozen tick and the paused clock.
  - A paused named save survives process restart with nursery, cash, and
    species mapping intact and the clock still paused.
- Live SIGTERM shutdown while paused: pause returned `paused: true`,
  checkpoint creation returned 200, then SIGTERM produced Uvicorn's orderly
  `Waiting for application shutdown / Application shutdown complete /
  Finished server process` sequence. Afterwards `world.sqlite3` held
  `clock_paused = 1` and one complete checkpoint directory was present.
  Shutdown is process-signal driven via `run.sh` (exec keeps signal
  forwarding to Uvicorn); there is no shutdown API endpoint, and none is
  claimed.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- `npm --prefix web run check/test/build` passed (5 frontend tests; no
  frontend changes in this slice).
