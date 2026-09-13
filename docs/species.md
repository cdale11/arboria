# Species catalog and scientific coverage

## 1. Catalog contract

Each record in `src/arboria/biology/species.py` includes `species_id`,
`schema_version`, scientific and common names, functional group,
photosynthetic pathway, site assignment, provenance, calibration status,
assimilation/water/growth coefficients, nutrient parameters, a reference
scenario, and supported/approximated/unsupported process lists, following the
record shape required by `docs/biology.md` section 10.

All six R1 records carry `calibration_status: "provisional"` with provenance
stating no inspected source backs the numbers. Coefficient magnitudes are
chosen for stable starter dynamics. Nothing in the catalog may be cited as a
measured species constant.

## 2. Sites

- `greenhouse`: sheltered bench, PAR 250 W/m².
- `outdoor`: open bed, PAR 400 W/m².

Site values are provisional forcing choices, not climate measurements.

## 3. Species and coverage

| Species | Group | Pathway | Site | Notes |
| --- | --- | --- | --- | --- |
| `ocimum_basilicum` (sweet basil) | herb | C3 | greenhouse | Fast starter growth; high N demand. Starter plant 1. |
| `solanum_lycopersicum` (tomato) | vegetable | C3 | greenhouse | Highest nutrient references; fruit/seed development unsupported. |
| `ficus_benjamina` (weeping fig) | houseplant tree | C3 | greenhouse | Medium rates; indoor foliage tree stand-in. |
| `crassula_ovata` (jade plant) | succulent | C3-modelled CAM plant | greenhouse | Lowest transpiration; CAM acid storage and succulent tissue unsupported — the C3 curve is an approximation, not a CAM model. |
| `juniperus_procumbens` (garden juniper) | bonsai-suitable conifer | C3 | outdoor | Slow growth; conifer foliage aggregated as a leaf cohort; wiring/pruning response unsupported. |
| `quercus_robur` (English oak) | outdoor tree | C3 | outdoor | Slow growth; masting and mycorrhizae unsupported. Starter plant 2. |

Shared R1 coverage for all six: organ topology, resource-bounded vegetative
growth, saturating assimilation, root-zone water, substrate N/P/K uptake,
deficiency stress, irreversible damage, and death. Shared unsupported R1
processes: sexual reproduction, thermal-time development, photoperiod and
dormancy, species morphology grammars, layered substrate chemistry, fertilizer
input, damage recovery, and pest/pathogen interaction.

## 4. Nursery composition

Starter plant 1 grows `ocimum_basilicum` in the greenhouse; starter plant 2
grows `quercus_robur` outdoors. The plant-to-species mapping is deterministic
catalog code, so checkpoints carry no extra species state. Starter geometry is
shared across species in R1; only coefficients and root N/P/K references vary
by species. Reference scenarios in `tests/unit/biology/test_species.py` run
each species through 200 ticks with periodic watering and require survival,
non-decreasing structural carbon, reserve accumulation, zone depletion, and
reservoir use.
