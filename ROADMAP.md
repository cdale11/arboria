# Arboria delivery roadmap

Status is evidence-based. `[x]` means the stated deliverable is complete; `[ ]` means not complete, including not started. All implementation releases are currently **not started**. Dependencies are sequential unless explicitly stated.

A coherent commit may finish an internal component; it does not finish a release. Each player-facing release must be independently runnable, documented, recoverable, and fully functional within its declared coverage. Do not expose unfinished controls, claim a partial release is complete, or substitute a prototype for its gates.

Items tagged `[AI/ML]` require AI, ML, neural-network, companion, or manager-learning systems to be wired.

## P0 — Planning baseline

Dependencies: user clarification and host inspection.

- [x] Record user choices and adopted defaults with unresolved evidence gates.
- [x] Define biology, architecture, learning, UI, economy, persistence, setup, and testing contracts.
- [x] Establish agent SOP, incident log, changelog, and dependency-ordered roadmap.
- [x] Validate documentation scope and local references.

Delivery evidence: [CHANGELOG.md](CHANGELOG.md). Git commit/push verification is reported with delivery; no application implementation or runtime validation is claimed.

## R1 — Complete living nursery foundation

Dependency: P0. This is the first playable release, not a skeleton server.

### Scope

#### Toolchain and launcher

- [x] Resolve and lock the baseline Conda Python/numerical/server/test stack. Evidence: `docs/evidence/R1-dependencies.md`.
- [x] Resolve and lock the environment-local npm TypeScript/Vite/Three.js/Vitest stack. Evidence: `docs/evidence/R1-dependencies.md`.
- [x] Select and lock browser e2e tooling compatible with the Conda/npm policy. Evidence: `docs/evidence/R1-ui-controls.md`.
- [x] Provide baseline `./run.sh` that activates `arboria`, prioritizes Conda Node/npm, builds the current frontend, and starts Uvicorn. Evidence: `docs/evidence/R1-launcher-server.md`.
- [x] Complete full R1 launcher gates: lock fingerprint synchronization, migration checks, interrupted-build recovery, offline repeat-start evidence, and failure-injection tests. Evidence: `docs/evidence/R1-launcher-gates.md` and `docs/evidence/R1-recovery.md`.

#### Access, ownership, and commands

- [x] Implement shared-password setup and session login/logout/status endpoints. Evidence: `docs/evidence/R1-auth-baseline.md`.
- [x] Implement CSRF tokens, same-origin unsafe-request checks, and baseline failed-login throttling. Evidence: `docs/evidence/R1-auth-hardening.md`.
- [x] Implement baseline data-directory process lock preventing two local server owners. Evidence: `docs/evidence/R1-process-lock.md`.
- [x] Implement authenticated single-world ownership metadata. Evidence: `docs/evidence/R1-world-metadata.md`.
- [x] Implement bounded command envelope, request epoch, deduplication, validation, and execution receipts. Evidence: `docs/evidence/R1-command-envelope.md`.
- [x] Implement bounded WebSocket/server-stream baseline for authenticated world/clock snapshot and ping messages. Evidence: `docs/evidence/R1-stream-baseline.md`.
- [x] Expose living-nursery projections through stream snapshots. Evidence: `docs/evidence/R1-living-nursery.md`.
- [x] Implement reconnect/resync behavior for biological projections and revisioned deltas. Evidence: `docs/evidence/R1-stream-resync.md`.

#### Time and world lifecycle

- [x] Implement server-owned in-memory 48× simulation clock with authenticated status, pause, resume, and speed controls. Evidence: `docs/evidence/R1-clock-baseline.md`.
- [x] Persist clock/world lifecycle state so restart resumes saved simulation time without wall-clock catch-up. Evidence: `docs/evidence/R1-world-metadata.md`.
- [x] Implement one-writer world loop consuming clock ticks at the documented 300-sim-second base tick. Evidence: `docs/evidence/R1-world-loop.md`.
- [x] Add lifecycle controls for pause/resume/save/restore/shutdown that remain serviceable while biological progression is paused. Evidence: `docs/evidence/R1-lifecycle.md`.
- [x] Implement minimal living-nursery tick with starter plants, biological projections, inspection, and lifecycle controls. Evidence: `docs/evidence/R1-living-nursery.md`.

#### Persistence and recovery

- [x] Implement SQLite metadata store. Evidence: `docs/evidence/R1-world-metadata.md`.
- [x] Implement immutable checkpoint generation layout. Evidence: `docs/evidence/R1-checkpoint-layout.md`.
- [x] Implement metadata-only named save creation and listing. Evidence: `docs/evidence/R1-named-saves.md`.
- [x] Implement metadata-only checkpoint restore with timeline/request-epoch rotation. Evidence: `docs/evidence/R1-metadata-restore.md`.
- [x] Implement metadata-only autosave checkpoints and status. Evidence: `docs/evidence/R1-metadata-autosave.md`.
- [ ] [AI/ML] Implement export/import and consistent world+learner checkpoint protocol.
- [x] Implement interrupted metadata-checkpoint generation cleanup on startup. Evidence: `docs/evidence/R1-interrupted-checkpoint-cleanup.md`.
- [x] Implement active metadata-checkpoint validation on startup. Evidence: `docs/evidence/R1-active-checkpoint-validation.md`.
- [x] Implement crash/disk-failure recovery and migration protocol. Evidence: `docs/evidence/R1-recovery.md`.
- [x] Add atomic-save failure-injection tests. Evidence: `docs/evidence/R1-recovery.md`.

#### Biology and species

- [x] Implement organ topology with stable IDs, acyclic parentage, cohort rules, and explicit resource pools. Evidence: `docs/evidence/R1-organ-topology.md`.
- [x] Implement baseline causal vegetative development driven by resources rather than decorative branch generation. Evidence: `docs/evidence/R1-vegetative-growth.md`.
- [x] Implement baseline bounded light-driven carbon assimilation for R1 coverage. Evidence: `docs/evidence/R1-carbon-assimilation.md`.
- [x] Implement water, N/P/K, root-zone environment, stress, damage, and death for R1 coverage. Evidence: `docs/evidence/R1-nursery-water.md` and `docs/evidence/R1-nutrient-stress.md`.
- [x] Implement baseline root-zone water with finite reservoir watering for R1 coverage. Evidence: `docs/evidence/R1-nursery-water.md`.
- [x] Implement N/P/K uptake, stress damage, and death for R1 coverage. Evidence: `docs/evidence/R1-nutrient-stress.md`.
- [x] Deliver six proposed representative species in outdoor/greenhouse zones with source-backed or explicitly provisional parameter metadata and reviewed scenarios. Evidence: `docs/evidence/R1-species.md`.
- [x] Document per-species supported, approximated, deferred, and unsupported processes. Evidence: `docs/species.md`.

#### Nursery, UI, and economy

- [x] [UI-01] Approve desktop/phone frames, visual direction, interaction states, and scene-first care journey. Artifact: `docs/ui-design-frames.md`; runtime implementation and browser evidence remain open.
- [x] [UI-02] Implement revision-qualified presentation state, coherent stream projections, reconnecting WebSocket consumption, snapshot replacement, and stale-delta resync. Evidence: frontend 29-test suite and server stream tests; native-browser evidence remains part of UI-10.
- [ ] [UI-03 through UI-10] Deliver the approved scene-first, detailed-stylized nursery UI, persistent shell, suggested editable care, shop previews, truthful companion controls, backup/recovery, and real-browser desktop/phone acceptance. Full specification and ordered dependencies: `docs/r1-ui-upgrade.md`.
- [ ] UI-03 initial selection state is now retained in the mounted client and marked on the selected plant card; focused inspector/navigation work remains open.
- [ ] Revalidate the baseline SVG projection and touch layout after the scene-first rebuild; current jsdom/layout evidence does not close this gate. Baseline evidence: `docs/evidence/R1-ui-controls.md`.
- [x] Implement minimal usable inspection, save, and clock controls for the living nursery. Evidence: `docs/evidence/R1-living-nursery.md`.
- [x] Implement real inventory, suppliers, purchases, demand-limited plant sales, and finite cash/material accounting. Evidence: `docs/evidence/R1-economy.md`.
- [x] Add economy tests for transaction consistency, duplicate sales, bounded demand, and anti-arbitrage. Evidence: `docs/evidence/R1-economy.md`.

#### Companion and learning

- [ ] [AI/ML] Implement competent full-authority caretaker for available actions, constrained by hard player protections. Partial baseline evidence: `docs/evidence/R1-companion.md` covers validated watering only; full authority and learned management remain open.
- [ ] [AI/ML] Implement real online neural prediction and preference learning with persisted model, optimizer, normalization, replay, RNG, and evaluation state.
- [ ] [AI/ML] Demonstrate R1 learning holdout and ablation evidence, including baseline-only fallback honesty.

#### Documentation and evidence

- [ ] Update README with actual setup/run/control/backup instructions after the UI upgrade; current baseline remains documented honestly. Evidence: `README.md` and `docs/evidence/R1.md`.
- [x] Produce `docs/evidence/R1.md` aggregating final R1 commands, versions, platform, scenario seeds, metrics, failures, limitations, and artifact locations. Evidence: `docs/evidence/R1.md`.
- [x] Keep CHANGELOG, ROADMAP, docs contracts, and MISTAKES synchronized with every delivered coherent change. Evidence: `CHANGELOG.md` and `docs/evidence/R1.md`.

### Mandatory gates

- [x] Unit/property/scenario/API/economy tests and Python/frontend static checks pass. Evidence: `docs/evidence/R1.md`.
- [ ] [AI/ML] Atomic-save failure injection and model/optimizer/replay continuation tests pass.
- [x] Launcher fresh/repeat/offline/setup interruption and authentication gates pass. Evidence: `docs/evidence/R1-launcher-gates.md` and `docs/evidence/R1.md`.
- [ ] Full playable loop browser tests and recorded real touch-device smoke test pass.
- [ ] [AI/ML] Learning holdout/ablation gates in `docs/testing.md` pass; baseline-only fallback honestly identified.
- [ ] Target-host 500-plant performance, 1,000-plant characterization, 24-real-hour soak, and ten-sim-year stability suite completed. Partial evidence: `docs/evidence/R1.md` records passing 500/1,000-plant latency and the full 500-plant ten-sim-year soak; only the 24-real-hour operational soak remains open.
- [ ] `docs/evidence/R1.md`, updated docs/changelog, reviewed commit, verified push. Evidence is current, but this gate remains open until full R1 blockers above are resolved.

R1 scope excludes sexual reproduction, advanced bonsai craft, layered chemistry/compost ecology, learned seasonal commercial planning, and experimental rule invention. Existing starter tree/bonsai forms are live biological stock, not evidence those later mechanics work. No later-feature controls appear until their release is functional.

## R2 — Reproduction, propagation, and inherited diversity

Dependency: R1.

### Development and reproductive biology

- [ ] Implement thermal-time development with explicit base/ceiling temperatures.
- [ ] Implement photoperiod, chilling/vernalization, dormancy, and senescence for supported species.
- [ ] Implement flowers/cones or documented analogous reproductive structures.
- [ ] Implement pollen/gamete viability, timing overlap, and supported pollination pathways.
- [ ] Implement fruit/seed development with carbon, water, and nutrient costs.
- [ ] Implement germination, viability decay, and storage-condition effects.
- [ ] Implement species-appropriate propagation methods for R2 species coverage.

### Genetics and selection

- [ ] Implement versioned quantitative-trait genotype records.
- [ ] Implement recombination, mutation distributions, dominance rules, and phenotype mapping.
- [ ] Enforce species/hybrid compatibility through validated compatibility records.
- [ ] Persist lineage, parentage, seed lots, cultivar identity, and RNG streams.
- [ ] Demonstrate at least one heritable selection response with a documented trade-off.
- [ ] Measure diversity and unintended correlated trait changes over fixed replicates.

### Products, economy, UI, and companion

- [ ] Add harvest/product inventory backed by produced biological material.
- [ ] Add sales for seeds, fruit, cuttings, and other R2 products through finite transactions.
- [ ] Add working breeding, pollination, seed-lot, lineage, propagation, harvest, and product UI flows.
- [ ] [AI/ML] Extend companion authority to supported propagation, pollination, seed management, and harvest actions.
- [ ] Display scientific coverage, compatibility, provenance, and unsupported reproductive behavior per species.

### R2 gates and evidence

- [ ] Validate reproductive resource conservation, inheritance distributions, compatibility, viability, and persistence.
- [ ] Add browser flows for breeding, lineage, propagation, harvest, and product sale.
- [ ] Add save migration/recovery tests for R2 schemas and lineages.
- [ ] Pass performance regression and multi-season soak gates.
- [ ] Publish `docs/evidence/R2.md`, update docs/changelog/roadmap, commit, push, and verify remote equality.

## R3 — Biological bonsai craft and structural horticulture

Dependency: R2.

### Structural interventions

- [ ] Implement shoot pruning that removes real topology, resources, and descendant organs.
- [ ] Implement root pruning that removes absorptive/storage structures and changes hydraulic risk.
- [ ] Implement bud response through source/sink and signaling effects.
- [ ] Implement defoliation with reserve cost, stress, regrowth, and mortality consequences.
- [ ] Implement wiring, unwiring, orientation changes, pressure damage, and timing effects.
- [ ] Implement repotting and root-zone/container architecture effects.
- [ ] Implement wound area, sealing, infection exposure, and transport consequences.
- [ ] Implement graft attempts, healing, compatibility, and transport connection before resource sharing.

### Bonsai UI, policies, and accounting

- [ ] Add precise mouse/touch branch/root selection and preview controls.
- [ ] Add consequence previews for pruning, root work, wiring, defoliation, repotting, and grafting.
- [ ] Add explicit protections for plants, structures, and destructive action classes.
- [ ] [AI/ML] Extend companion policies for structural interventions, including conservative defaults and protected exceptions.
- [ ] Account for removed material as cuttings, products, compost input, or waste without creating biomass.
- [ ] Preserve lineage and graft provenance through structural changes.

### R3 gates and evidence

- [ ] Validate topology integrity, mass/material conservation, wound progression, graft compatibility, and root/shoot stress response.
- [ ] Demonstrate species-dependent recovery and plausible mortality/stunting outcomes.
- [ ] Add browser flows for bonsai operations and mobile precise selection.
- [ ] Add save migration/recovery tests for structural/graft/wound state.
- [ ] Pass performance regression and unattended manager scenarios.
- [ ] Publish `docs/evidence/R3.md`, update docs/changelog/roadmap, commit, push, and verify remote equality.

## R4 — Soil, compost, disease, and ecological interaction

Dependency: R3.

### Substrate and nutrient chemistry

- [ ] Implement layered root-zone water storage, drainage, diffusion/advection, and leaching.
- [ ] Implement fertilizer items with explicit N/P/K and supported secondary/micronutrient composition.
- [ ] Implement nutrient transport, uptake, sorption, buffering, and bounded pH approximation.
- [ ] Implement oxygen availability and waterlogging effects on roots and microbes.
- [ ] Preserve open-system resource accounting for imports, drainage, gases, leachate, and discarded matter.

### Compost and soil ecology

- [ ] Implement compost feedstock records with water, carbon, nitrogen, degradable fractions, and provenance.
- [ ] Implement microbial functional groups, heat generation/loss, moisture, oxygen, and decomposition rates.
- [ ] Implement mineralization, leachate, maturity criteria, and usable compost products.
- [ ] Implement beneficial microbe interactions with resource costs and bounded benefits.
- [ ] Implement host-compatible pest/pathogen exposure, growth, spread, damage, and treatment effects.

### UI, companion, and transformations

- [ ] Add working compost, fertilizer, treatment, substrate-mixing, leachate, and soil-inspection UI flows.
- [ ] Add inventory transformations for composting, mixing, applying, discarding, and harvesting amendments.
- [ ] [AI/ML] Extend companion routines for compost maintenance, fertilizer scheduling, treatment, and outbreak response.
- [ ] Add state migration for substrate layers, ecology, pests/pathogens, and treatment histories.

### R4 gates and evidence

- [ ] Validate closed/open resource budgets for water, carbon, N/P/K, gases, leachate, and waste.
- [ ] Validate outbreak/treatment, compost maturity, oxygen stress, and fertilizer/leaching scenarios.
- [ ] Demonstrate at least three cross-system effects with reproducible causal traces and ablations.
- [ ] Add browser flows and regression tests for compost/fertilizer/treatment systems.
- [ ] Pass performance regression and multi-season soak gates.
- [ ] Publish `docs/evidence/R4.md`, update docs/changelog/roadmap, commit, push, and verify remote equality.

## R5 — Adaptive commercial shop management

Dependency: R4.

### Commercial learning and planning

- [ ] [AI/ML] Implement learned demand forecasting with customer cohorts, budgets, preferences, seasonality, and uncertainty.
- [ ] Implement bounded price exploration and quote expiry without synthetic random profit.
- [ ] Implement seasonal production, propagation, harvest, and inventory scheduling.
- [ ] Implement stock forecasting with storage, viability, spoilage, quality, and space constraints.
- [ ] [AI/ML] Implement higher-level manager planning over care, production, purchases, sales, and labor-saving decisions.
- [ ] Account for operating inputs, supplier limits, product quality, and real transaction constraints.

### Manager controls and explanations

- [ ] [AI/ML] Expose learned preferences, planning horizon, uncertainty, objectives, and policy overrides.
- [ ] [AI/ML] Add away reports covering plant changes, earnings, interventions, losses, risks, and learning updates.
- [ ] [AI/ML] Enforce player protections and cash/material constraints as hard constraints under all commercial planning.
- [ ] [AI/ML] Provide reset/freeze/baseline comparison controls for learned commercial behavior.

### R5 gates and evidence

- [ ] [AI/ML] Demonstrate multi-season autonomous operation with real transactions and no protection violations.
- [ ] [AI/ML] Compare learned manager against frozen/baseline managers over multiple fixed seeds.
- [ ] [AI/ML] Evaluate profit, mortality, inventory diversity, resource use, labor reduction, and uncertainty together.
- [ ] [AI/ML] Run anti-arbitrage, adversarial-policy, catastrophic-forgetting, migration, UI, performance, and soak tests.
- [ ] [AI/ML] Document failure cases and trade-offs rather than optimizing one headline metric.
- [ ] Publish `docs/evidence/R5.md`, update docs/changelog/roadmap, commit, push, and verify remote equality.

## R6 — Broad calibrated collection and scale

Dependency: R5. Species packages can be developed as complete internal changes earlier, but this scale release requires the full interacting systems.

### Species catalog expansion

- [ ] Revisit and confirm the exact expanded species list with the user before sourcing/implementation.
- [ ] Expand to a proposed baseline of at least 60 real species across trees, bonsai-suitable plants, herbs, vegetables, succulents, houseplants, and greenhouse/outdoor groups.
- [ ] Add per-species provenance, parameter uncertainty, process coverage, reference scenarios, and unsupported-behavior notes.
- [ ] Cover meaningful differences in architecture, seasonality, photosynthetic/water strategy, reproduction, substrate response, pruning response, and horticultural products.
- [ ] Avoid filling the count with reskins or generic unsupported parameters.

### Scale and rendering

- [ ] Meet 1,000-plant target-host tick/RAM gates with heterogeneous mature plants and overlapping canopies.
- [ ] [AI/ML] Include active learning, commerce, saves, manager behavior, and active client projections during scale tests.
- [ ] Demonstrate mobile visual scaling without changing server biology.
- [ ] Quantify browser FPS/memory on named desktop and mobile devices/settings.

### Optimization evidence

- [ ] Benchmark CPU vectorization, cohort algorithms, memory layouts, and thread settings.
- [ ] [AI/ML] Benchmark optional iGPU learning/render-adjacent workloads only if dependency and memory constraints allow.
- [ ] Adopt GPU use only with end-to-end evidence; otherwise document why CPU remains preferred.
- [ ] Keep optimized paths equivalent to reference kernels within documented tolerances.

### R6 gates and evidence

- [ ] Pass per-species biological/reference suites.
- [ ] Pass integrated multi-year scenarios, migration, regression, and 24-real-hour soak gates.
- [ ] Publish target-host performance metrics, browser/device metrics, bottlenecks, and residual limitations.
- [ ] Publish `docs/evidence/R6.md`, update docs/changelog/roadmap, commit, push, and verify remote equality.

## R7 — Validated emergent-rule laboratory

Dependency: R6; research gate, not guaranteed completion by a deadline.

### Research feasibility and policy

- [ ] [AI/ML] Resolve local proposal-generation feasibility and resource budget on the target machine.
- [ ] [AI/ML] Ask the user before adopting remote AI, ongoing external cost, new package-manager exceptions, or changed deployment requirements.
- [ ] Define opt-in world settings, risk warnings, rollback expectations, and unsupported guarantees.
- [ ] [AI/ML] Decide whether the generator is neural, evolutionary, search-based, symbolic, or hybrid using measured evidence.

### Proposal language and validator

- [ ] Implement a restricted typed, unit-aware proposal language for recipes, bounded interactions, and item definitions.
- [ ] Implement a bounded interpreter with no generated executable Python/JavaScript, imports, file/network access, or unbounded loops.
- [ ] Validate dimensions, resources, compatibility, dependencies, conservation, cost, and evaluation bounds.
- [ ] [AI/ML] Persist proposal provenance, generator checkpoint, parent rule-set hash, validation results, and rejection reasons.

### Isolated evaluation and activation

- [ ] Run proposals in isolated test worlds with fixed CPU/memory/tick budgets.
- [ ] Evaluate adversarial, conservation, stability, economy-exploit, and multi-season scenarios before activation.
- [ ] [AI/ML] Score novelty and usefulness separately from validity.
- [ ] Activate accepted rule sets only at checkpoint boundaries in opted-in worlds.
- [ ] Implement complete-world rollback to preactivation snapshots for failed active rules.

### R7 gates and evidence

- [ ] [AI/ML] Demonstrate an accepted new interaction/item transformation not individually scripted as a gameplay event.
- [ ] [AI/ML] Demonstrate rejected invalid proposals with reproducible reasons.
- [ ] [AI/ML] Show sustained bounded resource use and no validator bypass under adversarial generated proposals.
- [ ] Deliver opt-in laboratory UI, transparent limits, save compatibility, integration, soak, and performance evidence.
- [ ] Publish `docs/evidence/R7.md`, update docs/changelog/roadmap, commit, push, and verify remote equality.

If research gates fail, preserve in-progress status, publish the evidence, and consult the user. Do not replace this feature with random item naming or claim unrestricted scientific invention.

## Every-release completion checklist

- [ ] All advertised behavior implemented; no placeholders or disabled promised controls.
- [ ] Relevant scientific assumptions and sources reviewed; unresolved consequential questions asked.
- [ ] Applicable targeted and mandatory gates pass with recorded commands/results.
- [ ] README, CHANGELOG, ROADMAP, contracts, and actual incident log updated.
- [ ] Final diff reviewed for consistency, secrets, generated state, and unintended work.
- [ ] Intended files committed, pushed, and local/remote equality verified.
