# R1 species catalog — evidence

## Scope

- `src/arboria/biology/species.py` defines two sites (greenhouse PAR 250 W/m²,
  outdoor PAR 400 W/m²) and six validated species records with provisional
  provenance, calibration status, per-process coefficients, and
  supported/approximated/unsupported coverage lists.
- `src/arboria/sim/nursery.py` resolves each ticked plant to its catalog
  species (plant 1: `ocimum_basilicum` greenhouse; plant 2: `quercus_robur`
  outdoor) and uses species assimilation, water, nutrient, growth, and damage
  coefficients plus site PAR. Starter root N/P/K pools equal the species
  reference values. The mapping is deterministic, so checkpoint schema is
  unchanged.
- Projections, summaries, stream snapshots, and the web UI expose
  `species_id`, `site_id`, and `species_ids`.
- `docs/species.md` documents the catalog contract, sites, per-species
  coverage, nursery composition, and reference scenarios.

## Verification

- `python -m pytest tests/unit` passed with 106 tests, including catalog
  shape/provenance/coverage checks, site PAR ordering, unknown-ID rejection,
  and six reviewed per-species 200-tick watered scenarios asserting survival,
  structural maintenance, reserve accumulation, zone depletion, and reservoir
  use.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed with 5 tests.
- `npm --prefix web run build` passed.
