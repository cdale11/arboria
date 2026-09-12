# Arboria delivery roadmap

Status is evidence-based. `[x]` means the stated deliverable is complete; `[ ]` means not complete, including not started. All implementation releases are currently **not started**. Dependencies are sequential unless explicitly stated.

A coherent commit may finish an internal component; it does not finish a release. Each player-facing release must be independently runnable, documented, recoverable, and fully functional within its declared coverage. Do not expose unfinished controls, claim a partial release is complete, or substitute a prototype for its gates.

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
- [ ] Select and lock browser e2e tooling compatible with the Conda/npm policy.
- [x] Provide baseline `./run.sh` that activates `arboria`, prioritizes Conda Node/npm, builds the current frontend, and starts Uvicorn. Evidence: `docs/evidence/R1-launcher-server.md`.
- [ ] Complete full R1 launcher gates: lock fingerprint synchronization, migration checks, interrupted-build recovery, offline repeat-start evidence, and failure-injection tests.

#### Access, ownership, and commands

- [x] Implement shared-password setup and session login/logout/status endpoints. Evidence: `docs/evidence/R1-auth-baseline.md`.
- [x] Implement CSRF tokens, same-origin unsafe-request checks, and baseline failed-login throttling. Evidence: `docs/evidence/R1-auth-hardening.md`.
- [x] Implement baseline data-directory process lock preventing two local server owners. Evidence: `docs/evidence/R1-process-lock.md`.
- [ ] Implement authenticated single-world ownership metadata.
- [ ] Implement bounded command envelope, request epoch, deduplication, validation, and execution receipts.
- [ ] Implement bounded WebSocket/server-stream projection protocol and reconnect/resync behavior.

#### Time and world lifecycle

- [x] Implement server-owned in-memory 48× simulation clock with authenticated status, pause, resume, and speed controls. Evidence: `docs/evidence/R1-clock-baseline.md`.
- [ ] Persist clock/world lifecycle state so restart resumes saved simulation time without wall-clock catch-up.
- [ ] Implement one-writer world loop consuming clock ticks at the documented 300-sim-second base tick.
- [ ] Add lifecycle controls for pause/resume/save/restore/shutdown that remain serviceable while biological progression is paused.

#### Persistence and recovery

- [ ] Implement SQLite metadata store and immutable checkpoint generation layout.
- [ ] Implement autosave, named saves, restore, export/import, and consistent world+learner checkpoint protocol.
- [ ] Implement crash/disk-failure recovery and migration protocol.
- [ ] Add atomic-save failure-injection tests.

#### Biology and species

- [ ] Implement organ topology with stable IDs, acyclic parentage, cohort rules, and explicit resource pools.
- [ ] Implement causal vegetative development driven by resources rather than decorative branch generation.
- [ ] Implement light, carbon, water, N/P/K, root-zone environment, stress, damage, and death for R1 coverage.
- [ ] Deliver six proposed representative species in outdoor/greenhouse zones with source-backed or explicitly provisional parameter metadata and reviewed scenarios.
- [ ] Document per-species supported, approximated, deferred, and unsupported processes.

#### Nursery, UI, and economy

- [ ] Implement procedural 2.5D nursery rendering with generated assets and no gameplay dependence on visual level of detail.
- [ ] Implement usable desktop/touch inspection, care, protection, shop, save, and clock controls.
- [ ] Implement real inventory, suppliers, purchases, demand-limited plant sales, and finite cash/material accounting.
- [ ] Add economy tests for transaction consistency, duplicate sales, bounded demand, and anti-arbitrage.

#### Companion and learning

- [ ] Implement competent full-authority caretaker for available actions, constrained by hard player protections.
- [ ] Implement real online neural prediction and preference learning with persisted model, optimizer, normalization, replay, RNG, and evaluation state.
- [ ] Demonstrate R1 learning holdout and ablation evidence, including baseline-only fallback honesty.

#### Documentation and evidence

- [ ] Update README with actual setup/run/control/backup instructions for the playable release.
- [ ] Produce `docs/evidence/R1.md` aggregating final R1 commands, versions, platform, scenario seeds, metrics, failures, limitations, and artifact locations.
- [ ] Keep CHANGELOG, ROADMAP, docs contracts, and MISTAKES synchronized with every delivered coherent change.

### Mandatory gates

- [ ] Unit/property/scenario/API/economy tests and Python/frontend static checks pass.
- [ ] Atomic-save failure injection and model/optimizer/replay continuation tests pass.
- [ ] Launcher fresh/repeat/offline/setup interruption and authentication gates pass.
- [ ] Full playable loop browser tests and recorded real touch-device smoke test pass.
- [ ] Learning holdout/ablation gates in `docs/testing.md` pass; baseline-only fallback honestly identified.
- [ ] Target-host 500-plant performance, 1,000-plant characterization, 24-real-hour soak, and ten-sim-year stability suite completed.
- [ ] `docs/evidence/R1.md`, updated docs/changelog, reviewed commit, verified push.

R1 scope excludes sexual reproduction, advanced bonsai craft, layered chemistry/compost ecology, learned seasonal commercial planning, and experimental rule invention. Existing starter tree/bonsai forms are live biological stock, not evidence those later mechanics work. No later-feature controls appear until their release is functional.

## R2 — Reproduction, propagation, and inherited diversity

Dependency: R1.

- [ ] Implement phenology, flowers/fruit/seeds, supported pollination pathways, compatibility, germination, and species-appropriate propagation.
- [ ] Implement versioned genetics, recombination/mutation, phenotype trade-offs, lineage, and selection.
- [ ] Add harvest/product inventory and sales backed by produced material; companion handles supported propagation/harvest.
- [ ] Extend UI with working breeding/lineage/product workflows and scientific coverage information.
- [ ] Validate reproductive conservation, compatibility, inheritance distributions, seed persistence, and multi-generation diversity over fixed replicates.
- [ ] Demonstrate at least one heritable selection response with a documented cost/trade-off, not a scripted rarity bonus.
- [ ] Pass regression, new browser flows, save migration/recovery, performance regression, and multi-season soak gates; publish R2 evidence and commit/push.

## R3 — Biological bonsai craft and structural horticulture

Dependency: R2.

- [ ] Implement shoot/root pruning, bud response, defoliation, wiring/removal, wound progression, repotting/root architecture effects, and validated graft compatibility.
- [ ] Support consequence previews, explicit protected structures/actions, touch-friendly precise selection, and manager policies for structural interventions.
- [ ] Preserve mass/material and lineage through pruning/cuttings/grafts; no free branch/biomass generation.
- [ ] Demonstrate species-dependent recovery and structural response with plausible stress/mortality outcomes.
- [ ] Pass biological/regression/UI/migration/performance gates and unattended manager scenarios; publish R3 evidence and commit/push.

## R4 — Soil, compost, disease, and ecological interaction

Dependency: R3.

- [ ] Implement layered substrates and water/nutrient transport, fertilizer composition, buffering/pH approximation, oxygen and root-zone effects.
- [ ] Implement compost feedstocks, microbial functional groups, heat/moisture/oxygen, mineralization, leachate, maturity, and usable compost products.
- [ ] Add host-compatible pest/pathogen spread, treatments, and beneficial interactions with documented approximations.
- [ ] Complete compost/fertilizer/treatment UI, inventory transformations, companion routines, and state migration.
- [ ] Demonstrate at least three cross-system effects arising from shared processes, with reproducible causal traces and ablations.
- [ ] Pass closed/open resource budgets, outbreak/treatment/compost scenarios, regression/UI/performance and multi-season soak; publish R4 evidence and commit/push.

## R5 — Adaptive commercial shop management

Dependency: R4.

- [ ] Add learned demand, bounded price exploration, seasonal production/propagation scheduling, stock forecasting, and higher-level manager planning.
- [ ] Account for customer budgets/preferences, supply limitations, storage/viability, operating inputs, and product quality.
- [ ] Expose explanations, learned preferences, planning horizon, uncertainty, policy overrides, and away reports.
- [ ] Demonstrate multi-season autonomous operation with real transactions, no protection violations, and comparisons against frozen/baseline managers over multiple seeds.
- [ ] Evaluate profitability together with mortality, inventory diversity, resource use, and outcome uncertainty; document failure cases rather than optimizing one headline metric.
- [ ] Pass anti-arbitrage, adversarial-policy, catastrophic-forgetting, migration, UI, performance and soak gates; publish R5 evidence and commit/push.

## R6 — Broad calibrated collection and scale

Dependency: R5. Species packages can be developed as complete internal changes earlier, but this scale release requires the full interacting systems.

- [ ] Expand to a proposed baseline of at least 60 real species across the agreed categories, with per-species provenance, process coverage, and scenarios. Revisit the exact catalog with the user before sourcing/implementation; do not fill the count with reskins.
- [ ] Cover meaningful functional differences in architecture, seasonality, water strategy, reproduction, and horticultural response.
- [ ] Meet 1,000-plant target-host tick/RAM gates with heterogeneous mature plants, learning, commerce, saves, and active client projections.
- [ ] Demonstrate mobile visual scaling without changing server biology and quantify browser/device results.
- [ ] Benchmark CPU vectorization/cohort algorithms and optional iGPU learning; adopt GPU use only if end-to-end evidence supports it.
- [ ] Pass per-species suites, integrated multi-year scenarios, migration, regression and 24-hour soak; publish R6 evidence and commit/push.

## R7 — Validated emergent-rule laboratory

Dependency: R6; research gate, not guaranteed completion by a deadline.

- [ ] Resolve local proposal-generation feasibility and user-approved runtime/dependency requirements.
- [ ] Implement a restricted typed, unit-aware proposal language and bounded interpreter; no generated executable code.
- [ ] Implement isolated evaluation, conservation/compatibility/resource checks, novelty/usefulness assessment, versioned activation, complete-world rollback, and persistent provenance.
- [ ] Demonstrate an accepted new interaction/item transformation not individually scripted as a gameplay event, alongside rejected invalid proposals and reproducible evaluations.
- [ ] Show sustained bounded resource use and no validator bypass under adversarial generated proposals.
- [ ] Deliver opt-in laboratory controls, transparent limits, save compatibility, documentation, integration/soak/performance evidence and commit/push.

If research gates fail, preserve in-progress status, publish the evidence, and consult the user. Do not replace this feature with random item naming or claim unrestricted scientific invention.

## Every-release completion checklist

- [ ] All advertised behavior implemented; no placeholders or disabled promised controls.
- [ ] Relevant scientific assumptions and sources reviewed; unresolved consequential questions asked.
- [ ] Applicable targeted and mandatory gates pass with recorded commands/results.
- [ ] README, CHANGELOG, ROADMAP, contracts, and actual incident log updated.
- [ ] Final diff reviewed for consistency, secrets, generated state, and unintended work.
- [ ] Intended files committed, pushed, and local/remote equality verified.
