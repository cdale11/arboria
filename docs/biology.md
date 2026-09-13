# Functional–structural biology specification

## 1. Fidelity boundary

The model represents organs and selected physiological processes, not individual cells or complete molecular biochemistry. It aims for causal, internally consistent horticultural behavior with declared approximations. Predictive equivalence to real specimens requires calibration evidence and is not presumed.

Every species record lists supported processes, approximated processes, unsupported processes, provenance, parameter version, and validation scenarios. Unsupported does not mean "fake with a generic multiplier": never advertise a process that has not been implemented. The roadmap expands coverage through complete releases.

## 2. Units and state

Canonical units are SI unless explicitly named otherwise:

| Quantity | Unit / convention |
| --- | --- |
| Time | seconds internally; integer 300-second base ticks |
| Length, area, volume | m, m², m³ |
| Water, dry material, nutrient element | kg; each pool explicitly distinguishes material |
| Carbon | kg elemental C, not interchangeable with dry biomass |
| Temperature | °C in state/UI; convert explicitly to K for equations requiring it |
| Water potential | MPa, with sign convention documented per equation |
| Irradiance | W/m², distinguish photosynthetically active component |
| CO₂ | mol fraction or explicit µmol/mol, never unlabeled ppm |
| Relative humidity | fraction [0,1] |
| Nutrient concentration | kg element / m³ water |
| Conductance | Unit derived for its flux equation, stored in parameter metadata |
| Monetary amounts | integer minor units, outside biological kernels |

Water, carbon, N, P, and K are tracked separately. Biomass conversion factors specify dry-matter composition; structural carbon cannot be treated as both available carbohydrate and existing tissue. Atmospheric uptake/release, evaporation, drainage, imports/exports, and discarded material appear as explicit boundary fluxes.

Plant state includes developmental age, organ topology, genotype modifiers, resource pools, hydraulic stress, damage, and phenology. Substrate state includes volume, water, drainage capacity, oxygen proxy, mineral pools, temperature, and later organic pools/pH/buffering. Climate state includes temperature, humidity, radiation, rain, and wind proxies.

Implemented R1 baseline biology currently includes pure organ topology validation and explicit resource pools only. `Organ` records have positive stable IDs, plant IDs, optional parent IDs, organ kind, created tick, developmental stage, geometry fields, alive/damage state, cohort count, and separate structural carbon, reserve carbon, water, nitrogen, phosphorus, and potassium pools. Validation rejects duplicate IDs, missing/cross-plant parents, cyclic parentage, nonfinite values, negative geometry/resources, invalid damage fractions, and non-cohort aggregate counts. Growth, light, water uptake, nutrient uptake, stress, damage progression, death, species parameters, persistence integration, and UI drive the slices below.

Implemented R1 vegetative growth currently applies resource-bounded elongation to existing structural organs only. Growth demands debit reserve carbon, water, nitrogen, phosphorus, and potassium from the plant root organ, scale all demands by the limiting available resource, add structural carbon and associated material to the target organ, and never create new organs. Light-driven assimilation, root/substrate uptake, allocation priorities, organ initiation, stress responses, death, species grammars, and persistence integration remain unimplemented.

Implemented R1 carbon assimilation currently uses the documented provisional saturating light response for live leaf cohorts. It adds atmospheric carbon uptake to the plant root reserve-carbon pool and reports the boundary flux. Temperature, water, and nutrient response factors are bounded `[0,1]`. This is not a Farquhar, C4, or CAM model. Canopy shading, root/substrate uptake, nutrient chemistry, respiration, stress, damage, death, and species calibration remain unimplemented.

Implemented R1 living nursery currently ticks two deterministic starter plants through zone-coupled water exchange, water-stressed assimilation, substrate N/P/K uptake, deficiency stress, irreversible damage, and death. Each plant owns a well-mixed 0.20 kg root zone starting at 0.12 kg plus finite substrate N/P/K starting at 0.020/0.0040/0.0080 kg with no fertilizer input; a finite 2.0 kg reservoir supplies receipt-backed watering commands with a 0.05 kg per-command limit and explicit drainage. Live nutrient stress feeds assimilation; combined water/nutrient stress below 0.5 accrues organ damage and kills at damage 1.0, and dead plants stop ticking. Nursery organs, water zones, nutrient zones, and reservoir persist in checkpoint state and recover on restore/startup. Layered substrate, waterlogging, fertilizer input, damage recovery, and calibration remain unimplemented.

## 3. Generic update rules

For a conserved pool `x` in kg:

```text
x_next = x + dt_s * (sum(inflow_kg_s) - sum(outflow_kg_s))
```

Bound fluxes before integration using donor supply, receiver capacity, and competing demand. Do not compute negative pools and silently clamp away the conservation error. Allocation of a shared resource must be joint, deterministic in tie handling, and insensitive to arbitrary array ordering.

Use float64 accounting and compensated sums where error measurements justify them. Tests define tolerances in both absolute units and relative scale. An initial numerical target is absolute residual ≤1e-10 kg plus 1e-8 times total participating mass per isolated kernel update; this is an engineering tolerance, not biological accuracy. Measure long-run residuals separately and document stricter/looser bounds with cause.

Reject NaN/Inf at catalog/input boundaries. On unexpected numerical failure, preserve the last valid checkpoint, record diagnostics, and pause with an actionable error. Never continue a corrupted world by filling numbers with zero.

## 4. Light and carbon — R1 core

Canopy interception may begin with layer-based Beer–Lambert attenuation:

```text
I_below = I_above * exp(-k_extinction * leaf_area_index)
```

`k_extinction` is dimensionless, leaf-area index is m² leaf/m² ground, and shading partitions available radiation between plants rather than giving each the unattenuated total. The spatial grid and vertical layers must be fine enough to distinguish moving a plant into shade. Rendering shadows are not the authoritative light model.

R1 may use an explicitly provisional saturating assimilation response:

```text
gross_C_rate = leaf_area_m2 * Amax_kgC_m2_s
               * I_PAR / (I_PAR + K_I)
               * f_temperature * f_water * f_nutrient
```

Response factors are bounded [0,1] and require species-specific provenance/calibration. This is not a mechanistic Farquhar model and cannot be labeled one. Net gain subtracts maintenance/growth respiration, recorded as atmospheric carbon release. Temperature response must have finite lower/upper limits; do not use unbounded exponential rates.

CAM plants require a distinct documented day/night uptake/storage approximation, not the C3 curve relabeled. Model stored organic-acid carbon explicitly if implementing nighttime uptake. More detailed C3/C4/CAM physiology is a future coverage extension with its own evidence; do not silently universalize one pathway.

## 5. Water and nutrients — R1 core, R4 refinement

Root water uptake depends on root absorptive area, substrate availability, hydraulic conductance, and plant water status. A bounded conductance form is acceptable:

```text
uptake_kg_s = conductance_kg_s_MPa * max(0, psi_soil_MPa - psi_root_MPa)
```

Couple this to substrate depletion and plant hydraulic capacity. Transpiration depends on leaf area, vapor pressure deficit, light, and stomatal response. Zero light is not necessarily zero water loss. Severe water deficit changes stomata before structural death; accumulated damage and recovery have explicit rates and thresholds.

Watering adds actual inventory water to a specified root zone. Above-capacity water drains with dissolved nutrients and optional leachate collection. Waterlogging reduces oxygen supply and root function. Fertilizing adds an item-defined nutrient composition; N, P, K cannot be created from a generic fertility score.

Nutrient uptake may use bounded saturation kinetics `Vmax * concentration / (Km + concentration)`, with units and temperature/root modifiers explicit. Plant growth is limited jointly by assimilate, water status, nutrient availability, and developmental capacity. Luxury uptake, if supported, uses finite storage pools.

R1 root zone may be well-mixed per container/bed cell. R4 adds vertical layers, diffusion/advection, sorption, pH/buffering, mineralization, and oxygen-dependent decomposition. Bed cells shared by plants must conserve resources across all users.

## 6. Architecture and allocation

Developmental grammars specify allowed organ production and branching patterns. A bud proposes a growth demand; physiology determines affordable elongation/leaf initiation. Insufficient resources delay, reduce, or abort development according to the species model. Never spawn geometry then invent biomass to match it.

Allocate to maintenance before discretionary growth; reserve mobilization and starvation rules are explicit. Allocation priorities depend on phenology, source/sink strength, stress, and simplified signaling. Hormone proxies have bounded production/transport/decay and named interpretations; do not label an arbitrary growth multiplier "auxin simulation".

Roots branch within substrate geometry. Root cohorts may aggregate fine absorptive roots, but preserve zone occupancy, age distribution, and absorptive area. A pot limits available volume, not merely a global growth multiplier.

Leaves and roots can form cohorts when equivalent in environment and developmental state. Splitting/merging preserves area, mass, reserves, nutrients, age distribution approximation, and provenance. Structural branches and editable buds remain explicit. Maximum organ budgets cannot silently halt growth: implement validated cohort coarsening or report a capacity gate.

## 7. Development and reproduction — R2

Use thermal time with explicit base/ceiling temperatures, photoperiod response, vernalization/chilling where relevant, and age/resource thresholds. Senescence moves recoverable nutrients to reserves and the remainder to litter. Dormancy cannot be represented solely by switching visible leaves off.

Reproduction requires flowers/cones or supported analogous structures, viable gametes, timing overlap, and species compatibility. Pollen transport may be a zone-level agent/flux approximation with explicit probabilities. Seed set spends carbon and nutrients. Seed viability decays with documented storage conditions.

Genetics begins with a versioned, species-bounded quantitative-trait representation: loci/alleles, dominance rules, recombination map approximation, mutation distributions, and phenotype mapping. Mutations change traits within documented viable ranges and have trade-offs. Cross-species hybridization is allowed only by validated compatibility data, not name matching or arbitrary embedding similarity.

All RNG streams are persisted; evolution is stochastic but reproducible within the supported execution contract. Selection results must be measured over replicates, including genetic diversity and unintended correlated effects.

## 8. Bonsai and injury — R3

- Pruning removes actual topology and resource pools; products become inventory or waste with accounting.
- Bud release follows signaling/source–sink changes and species bud availability.
- Root pruning reduces actual absorptive structures and storage, changing hydraulic risk.
- Wiring changes segment orientation over a bounded interval; excessive pressure/time can damage tissue.
- Wounds have area, sealing progression, infection exposure, and transport effects.
- Grafts require compatibility, contact, healing time, and successful transport connection before sharing resources.
- Defoliation spends regrowth reserves and affects survival; no guaranteed miniaturization bonus.

Mechanical growth is a bounded structural approximation, not full finite-element wood mechanics. Document unsupported failures such as detailed wind fracture until implemented.

## 9. Soil ecology and pests — R4

Compost tracks feedstock water, carbon, nitrogen, degradable fractions, microbial functional-group biomass, temperature, and oxygen. Decomposition produces heat and explicit gas/leachate losses. Maturity is inferred from modeled state; elapsed time alone is insufficient.

Pathogens/pests need host compatibility, exposure, growth/reproduction, damage, spread, and treatment effects. Beneficial microbes have resource demands and bounded benefits. Avoid a universal disease dice roll unrelated to conditions. Detailed microbial species taxonomy and biochemical pathways are unsupported unless added with evidence.

## 10. Species catalog and scientific evidence

Each record must include:

```text
species_id, schema_version, scientific_name, common_names
functional_group, photosynthetic_pathway, morphology_grammar_version
parameter_values {value, unit, provenance_id, uncertainty, calibration_status}
developmental_rules, compatibility_data, supported_processes
approximations, unsupported_processes, reference_scenarios
```

Sources must be actually inspected. Store title/author/date, URL or bibliographic identifier, access date, applicable species/conditions, extracted quantity and units, and conversion rationale. No source was used to validate numerical biological coefficients in this planning deliverable; none are presented as measured species constants.

Calibration data and evaluation data must be distinct when fitting parameters. Numerical stability does not prove biological validity. Publish per-species coverage and error/qualitative-response evidence before shipping that species.
