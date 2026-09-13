# R1 Living Nursery Evidence

## Scope

- Added pure `arboria.sim.nursery` starter state with two deterministic plants.
- Each plant has root, stem, and 8-count leaf cohort organs.
- World ticks advance bounded carbon assimilation followed by resource-bounded stem growth.
- Assimilation uses provisional `Amax=1e-6 kgC/m2/s`, `PAR=250 W/m2`, `K_I=120 W/m2`.
- Temperature, water, and nutrient factors are fixed at `1.0` as uncalibrated placeholders.
- Per-tick stem demand uses 0.1% of root reserve carbon plus small water/nutrient fractions.
- Added authenticated `/api/v1/plants` and `/api/v1/plants/{id}` projections.
- Added nursery summary to `/api/v1/world` and stream snapshots.
- Added nursery organs to checkpoint `state.json` with restore/startup recovery.
- Added minimal frontend inspection rendering with honest unimplemented-system notice.

## Evidence

- `python -m pytest tests/unit` passed with 80 tests.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed.
- `npm --prefix web run build` passed.

## Limitations

- No water/nutrient uptake, root-zone environment, stress, damage, death, species catalog, economy, companion, reconnect deltas, procedural 2.5D rendering, touch controls, or shop UI exists yet.
- Forcing and assimilation parameters are provisional and uncalibrated.
- Only two starter plants exist; no planting, watering, fertilizing, sales, or management actions exist yet.
