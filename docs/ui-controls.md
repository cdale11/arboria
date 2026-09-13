# Browser controls contract

## 1. Scope

The R1 browser app (`web/src/main.ts`) provides usable controls over
the authenticated JSON API. Every control calls a real endpoint and reports
the receipt or error honestly in a status region; no button is decorative and
no promised control is disabled.

- Care per plant: inspect (organ kind, alive, damage detail), water 0.02 kg
  via `nursery.water`, protect/unprotect via `nursery.protect` and
  `nursery.unprotect`, and sell via `shop.sell_plant`. Protected plants are
  rejected by server validation if sold before unprotection.
- Shop: buy 0.5 kg reservoir water via `shop.buy_water`; buy a plant of the
  selected demanded species via `shop.buy_plant`.
- Clock: pause, resume, and speed selection (1x, 12x, 48x, 144x) within the
  server-validated 1–144 range.
- Saves: immediate checkpoint, named save with a required non-empty name,
  restore from the listed named saves, current-domain export/import archive
  controls, and manual refresh.
- Rendering: a generated SVG nursery scene projects plant height, canopy size,
  stress/alive status, and protection state from server projections. It is a
  visual projection only; simulation, sales, and care do not depend on whether
  the SVG is rendered.
- Commands are sent with a fresh UUID, the current world/timeline/epoch
  snapshot (re-fetched per command so post-restore timelines stay valid),
  and the readable CSRF cookie. Missing CSRF fails fast with a reload
  hint. Rejected commands display the server reason.

## 2. Touch layout

- `web/index.html` enforces a responsive viewport, wrapping text, and 44 CSS
  pixel minimum heights on buttons, inputs, and selects.
- At narrow widths, controls stack to the available width so primary care,
  shop, clock, and save actions remain reachable without hover-dependent
  interaction.
- This is automated layout-contract coverage only. No physical-device smoke
  test has been run, and no mobile performance claim is made.

## 3. Deferred

Fertilizer flows, companion settings, learner-inclusive export/import,
keyboard/reduced-motion audits, and physical touch-device validation are not
implemented. Browser e2e currently uses the locked Vitest/jsdom stack rather
than native browser binaries.
