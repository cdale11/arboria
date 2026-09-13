# R1 Carbon Assimilation Evidence

## Scope

- Added pure `arboria.biology.carbon` bounded light-driven carbon assimilation kernel.
- Implemented the provisional saturating response documented in `docs/biology.md` for live leaf cohorts.
- Added bounded temperature, water, and nutrient stress factors.
- Added atmospheric carbon boundary-flux reporting and reserve-carbon addition to plant root organs.
- Preserved noncarbon resource pools during assimilation.

## Evidence

- `python -m pytest tests/unit/biology` passed with 17 tests.
- `ruff check src/arboria/biology tests/unit/biology` passed.
- `mypy src tests/unit` passed.

## Limitations

- This is a provisional R1 carbon-assimilation kernel only.
- No canopy shading, root/substrate uptake, nutrient chemistry, respiration, stress, damage, death, species calibration, persistence integration, commands, or UI are implemented yet.
