# R1 baseline caretaker companion evidence

## Implemented

- `src/arboria/sim/companion.py` contains a deterministic baseline caretaker
  policy over authoritative `PlantProjection` records.
- The policy prioritizes the lowest water-stress live plant, respects a bounded
  per-tick action budget, and proposes only the existing bounded
  `nursery.water` command.
- The caretaker never proposes plant sales. Protected plants remain protected
  from destructive sale actions; watering is ordinary care and does not bypass
  the server's resource validation.
- `GET /api/v1/companion` exposes current baseline policy/counters.
- `POST /api/v1/companion` changes the explicit enabled state, threshold, and
  action budget with authenticated CSRF protection.
- `POST /api/v1/companion/run` creates companion-owned commands and submits them
  through the ordinary `CommandService` and `apply_command` validation path.
- The browser exposes enable/disable and “Check plants now” controls with the
  latest structured decision reason.

## Verification

- Pure policy tests cover low-water prioritization, bounded/no-action behavior,
  and invalid action budgets.
- API tests cover authenticated settings, companion execution, applied receipt,
  `actor: companion`, and `kind: nursery.water`.
- Frontend tests cover companion control presence and run dispatch.

## Explicit limits

- This is baseline deterministic care, not neural prediction or preference
  learning. It does not claim learned improvement, model persistence, replay,
  optimizer, normalization, RNG, holdout, or ablation evidence.
- Policy/counter persistence across restart is not yet implemented; the
  current-domain checkpoint remains honest about that limitation.
- The caretaker currently uses water care only. Fertilizer, relocation,
  propagation, harvest, and later-release actions remain unavailable.
