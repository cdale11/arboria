# R1 browser nursery controls — evidence

## Scope

- `web/src/main.ts` mounts an interactive nursery app: per-plant
  inspect/water/protect/unprotect/sell, shop buy-water/buy-plant with a
  species dropdown, clock pause/resume/speed, checkpoint/named-save/restore/
  refresh, a plant organ detail panel, and an honest result status region.
- `createApiClient` wraps the JSON API with CSRF headers, per-command world
  snapshot refresh, envelope construction, and strict response-shape
  validation.
- `src/arboria/app/server.py` persists protected plant IDs in checkpoints,
  exposes them in list/detail projections, and rejects sale of protected
  plants until unprotected.
- `web/index.html` sets responsive viewport/layout CSS and 44 CSS-pixel
  minimum heights on controls for the 360px touch-layout contract.
- `web/package.json` makes `npm --prefix web run test:e2e` a real locked
  Vitest/jsdom full-flow check instead of a placeholder failure.

## Verification

- `python -m pytest tests/unit/app/test_shop_api.py tests/unit/app/test_launcher.py` passed with 15 tests.
- `npm --prefix web run test` passed with 18 tests, including command
  envelope/CSRF-header shape, fail-fast without CSRF, control presence,
  water/protect/unprotect/sell/shop/clock/save/restore dispatch with
  arguments, rejection messaging, organ detail display, and required save-name
  validation.
- `npm --prefix web run test:e2e` passed with one jsdom full-flow test covering
  inspect, water, protect/unprotect, sale, pause/resume, and checkpoint.

## Limitations

- Browser e2e is implemented with the locked Vitest/jsdom stack. Native browser
  automation and physical touch-device smoke validation have not been run.
- Procedural 2.5D rendering, fertilizer flows, companion settings, keyboard/
  reduced-motion audits, and export are still deferred.
