# R1 desktop nursery controls — evidence

## Scope

- `web/src/main.ts` mounts an interactive nursery app: per-plant
  inspect/water/sell, shop buy-water/buy-plant with a species dropdown,
  clock pause/resume/speed, checkpoint/named-save/restore/refresh, a plant
  organ detail panel, and an honest result status region.
- `createApiClient` wraps the JSON API with CSRF headers, per-command world
  snapshot refresh, envelope construction, and strict response-shape
  validation. `docs/ui-controls.md` records the controls contract and
  deferred touch/protection/rendering work.

## Verification

- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed with 16 tests, including command
  envelope/CSRF-header shape, fail-fast without CSRF, control presence,
  water/sell/shop/clock/save/restore dispatch with arguments, rejection
  messaging, organ detail display, and required save-name validation.
- `npm --prefix web run build` passed.
- `python -m pytest tests/unit` passed with 128 tests (no backend changes in
  this slice).
- Live server check: authenticated `/api/v1/plants` serves projections and
  the built bundle contains the control actions.
