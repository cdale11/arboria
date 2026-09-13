# R1 Organ Topology Evidence

## Scope

- Added pure biology module `arboria.biology.organs` with no app, SQL, network, clock, or rendering imports.
- Added organ kinds for R1 structural organs and leaf/root cohorts.
- Added explicit resource pools for structural carbon, reserve carbon, water, nitrogen, phosphorus, and potassium.
- Added organ/topology validation for positive stable IDs, one root organ per plant, existing same-plant parents, acyclic parentage, finite nonnegative geometry/resources, bounded damage, and cohort-count rules.
- Added resource-pool summation that keeps each material separate.

## Evidence

- `python -m pytest tests/unit/biology/test_organs.py` passed with 7 tests.
- `ruff check src/arboria/biology tests/unit/biology` passed.
- `mypy src tests/unit` passed.

## Limitations

- This is the biology state/invariant baseline only.
- No growth, light, carbon assimilation, water/nutrient uptake, stress, damage progression, death, species catalog, persistence integration, commands, or UI are implemented yet.
