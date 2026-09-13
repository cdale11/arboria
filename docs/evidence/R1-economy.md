# R1 shop economy — evidence

## Scope

- `src/arboria/sim/economy.py` implements integer-minor-unit cash, the
  provisional price table, finite per-species buyer demand, reservoir refill
  with a 5.0 kg cap, and payload round-trip with starter fallback.
- `src/arboria/sim/nursery.py` adds real plant inventory operations:
  `add_starter_plant` builds live starter topology with fresh IDs and starter
  zones, `remove_plant` drops a live plant with its zones and mapping, and
  the plant-to-species mapping persists in checkpoint schema 4.
- `/api/v1/commands` serves `shop.buy_water`, `shop.buy_plant`, and
  `shop.sell_plant` through the bounded envelope with receipts. Projections,
  summaries, stream snapshots, and the web UI expose cash and demand.
- `docs/economy.md` records the money, pricing, command, and persistence
  contract.

## Verification

- `python -m pytest tests/unit` passed with 128 tests, including kernel
  conservation/rejection tests, structural buy-then-sell loss for every
  species, demand exhaustion, unknown/dead/duplicate sales, duplicate
  `command_id` single-application, and checkpoint/restore preservation of
  cash, demand, reservoir, and bought plants.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed with 5 tests.
- `npm --prefix web run build` passed.
