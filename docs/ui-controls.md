# Browser controls contract

## 1. Scope

The R1 browser app (`web/src/main.ts`) provides usable desktop controls over
the authenticated JSON API. Every control calls a real endpoint and reports
the receipt or error honestly in a status region; no button is decorative and
no promised control is disabled.

- Care per plant: inspect (organ kind, alive, damage detail), water 0.02 kg
  via `nursery.water`, sell via `shop.sell_plant`.
- Shop: buy 0.5 kg reservoir water via `shop.buy_water`; buy a plant of the
  selected demanded species via `shop.buy_plant`.
- Clock: pause, resume, and speed selection (1x, 12x, 48x, 144x) within the
  server-validated 1–144 range.
- Saves: immediate checkpoint, named save with a required non-empty name,
  restore from the listed named saves, and manual refresh.
- Commands are sent with a fresh UUID, the current world/timeline/epoch
  snapshot (re-fetched per command so post-restore timelines stay valid),
  and the readable CSRF cookie. Missing CSRF fails fast with a reload
  hint. Rejected commands display the server reason.

## 2. Deferred

Touch-target sizing and small-screen layout review, plant protection
controls, procedural 2.5D rendering, fertilizer flows, companion settings,
and export are not implemented. The game-design 44px touch target and
360px-wide layout requirements remain open and are tracked on the roadmap.
