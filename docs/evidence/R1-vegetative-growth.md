# R1 Vegetative Growth Evidence

## Scope

- Added pure `arboria.biology.growth` resource-bounded vegetative growth kernel.
- Growth applies only to existing structural organs (`root`, `stem`, `branch`).
- Growth demands are finite and nonnegative, target existing organs, and cannot repeat target IDs.
- The kernel scales requested growth by the limiting root-held reserve carbon, water, nitrogen, phosphorus, or potassium.
- Growth debits root pools and increments existing target organ length/resources; it does not create branches or organs.

## Evidence

- `python -m pytest tests/unit/biology` passed with 12 tests.
- `ruff check src/arboria/biology tests/unit/biology` passed.
- `mypy src tests/unit` passed.

## Limitations

- This is a baseline growth-accounting kernel only.
- No photosynthesis, root/substrate uptake, light model, nutrient chemistry, organ initiation, stress/damage/death, species grammars, persistence integration, commands, or UI are implemented yet.
