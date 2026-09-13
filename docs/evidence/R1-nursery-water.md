# R1 Nursery Water Evidence

## Scope

- Added pure `arboria.biology.water` well-mixed root-zone kernel.
- Each starter plant owns a 0.20 kg-capacity zone starting at 0.12 kg.
- Ticks apply bounded zone-to-root uptake, leaf transpiration, and above-capacity drainage.
- Per-plant assimilation water factor now comes from live zone fullness instead of fixed 1.0.
- Added finite 2.0 kg reservoir; `nursery.water` transfers reservoir water into a zone.
- Per-command watering limit is 0.05 kg; over-reservoir and unknown-plant requests are rejected.
- Watering runs through the receipt-backed `/api/v1/commands` path with deduplication.
- Zones and reservoir persist in checkpoint state with restore/startup recovery.
- Plant projections expose zone water and stress; UI shows zone/reservoir totals.

## Evidence

- `python -m pytest tests/unit` passed with 87 tests.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed with 5 tests.
- `npm --prefix web run build` passed.
- Live smoke test: authenticated `/api/v1/plants` returned 2 plants/6 organs with zone water; authenticated `/` served the built bundle containing the nursery loader.

## Limitations

- No nutrient uptake/chemistry, layered substrate, pH, oxygen/waterlogging effects, rainfall, humidity/VPD coupling, stress damage, death, species calibration, economy, companion, or irrigation automation exists yet.
- Forcing, conductance, transpiration, and starter zone/reservoir values are provisional and uncalibrated.
- Watering applies immediately through the command path, including while paused; no queued resume-time horticultural scheduler exists yet.
