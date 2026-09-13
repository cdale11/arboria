# R1 nutrient uptake, stress damage, and death — evidence

## Scope

Pure N/P/K kernels plus nursery integration:

- `src/arboria/biology/nutrients.py` implements well-mixed per-plant substrate
  N/P/K, bounded first-order root uptake into finite luxury pools, a
  Liebig-minimum deficiency factor in `[0,1]`, and irreversible stress-damage
  accumulation with death at damage 1.0.
- `src/arboria/sim/nursery.py` gives each starter plant finite substrate N/P/K
  (0.020/0.0040/0.0080 kg), runs uptake every tick, feeds the live nutrient
  factor into assimilation, accrues organ damage while combined water/nutrient
  stress sits below 0.5, and skips dead plants in later ticks.
- Projections expose `alive`, `damage_fraction`, `nutrient_stress_factor`, and
  per-plant zone N/P/K; summaries expose zone N/P/K totals and dead plants.
- Checkpoint state carries `nursery_nutrient_zones` (schema version 3);
  restore/startup fall back to starter values for older checkpoints.
- The web inspection UI renders zone N/P/K, damage, and dead-plant counts.

## Provisional calibration

All nutrient parameters are explicitly provisional, not measured species
constants: uptake rate 1.0e-4/s, references matching starter root mobile pools
(N 0.0010, P 0.00020, K 0.00040 kg), luxury capacity at twice the reference,
damage threshold 0.5, and damage rate 1.0e-6/s (a fully starved plant dies in
roughly 3,300 ticks). There is no fertilizer input, no damage recovery, no
layered substrate, no waterlogging, and no species calibration in R1.

## Verification

- `python -m pytest tests/unit` passed with 96 tests, including kernel bounds
  (zone-supply and capacity limits), limiting-nutrient stress, damage
  accrual/irreversibility/death, 50-tick zone depletion, 20,000-tick
  starvation death with dead plants holding still, nutrient payload round-trip
  and starter fallback, and API checkpoint/restore preservation.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed with 5 tests.
- `npm --prefix web run build` passed.
