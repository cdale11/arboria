# Verification and acceptance specification

No application tests exist in the planning baseline. The suites and commands below are requirements for implementation, not reported results.

## 1. Test organization and tools

Candidate tools: pytest, Hypothesis, Python type checking and linting through Conda; TypeScript checks and browser tests through the authorized npm environment. Browser binaries/native dependencies must have an explicit setup path compatible with the user's environment policy. Ask if the available tools cannot satisfy it; do not invoke an unapproved system package installer.

R1 must document and make these intended commands real, or document a justified equivalent before delivery:

```bash
python -m pytest tests/unit tests/integration tests/persistence tests/scenarios
python -m pytest tests/performance -m performance
npm --prefix web run check
npm --prefix web run test
npm --prefix web run test:e2e
npm --prefix web run build
./run.sh
```

All run inside activated `arboria`; `run.sh` also activates it internally. A CI job or documented local gate must run lint/types, numerical tests, save/recovery, frontend build, browser flows, and release-specific scenarios. Do not use arbitrary percentage coverage as a substitute for checking invariants and failure boundaries.

## 2. Numerical and biological tests

| Test family | Required evidence |
| --- | --- |
| Mass balance | Closed-system conservation; explicit atmospheric/drainage/import/export residuals |
| Water | Drying, rewatering, saturation/drainage, shared-root-zone competition, waterlogging |
| Carbon | Dark respiration, light saturation, reserve mobilization, starvation, growth cost |
| Nutrients | Donor-limited uptake, deficiency response, fertilizer composition, leaching |
| Topology | No cycles, valid parentage, pruning descendants, mass-preserving cohort changes |
| Order independence | Stable results under equivalent array/storage reorder, within declared tolerance |
| Time integration | Base tick versus refined substeps; stability under forcing changes |
| Species | Each advertised process has a per-species reference scenario and provenance |
| Seasons | Photoperiod, dormancy/chilling when supported, hemisphere/phase configuration |
| Reproduction (R2) | Compatibility, fertility/viability, inheritance, seed/fruit resource cost |
| Bonsai (R3) | Root/shoot pruning consequences, wiring damage, wounds, graft validity |
| Ecology (R4) | Compost material/heat accounting, oxygen constraints, host-specific spread |

Property-based tests vary valid input ranges and boundary values. Metamorphic checks include unchanged biology when rendering disabled, equivalent explicit resource partitioning, and save/load continuation. Do not assert simplistic global monotonicity where competing processes make it scientifically false.

A golden trajectory must record parameters, sources, engine version, RNG configuration, and tolerance rationale. Changing it requires an explained cause, not merely accepting new output.

## 3. Learning tests

- Analytical/autodiff or finite-difference checks of small-network gradients against independent expectations.
- Finite and bounded predictions, zero-variance normalization, missing features, out-of-range observations.
- Chronological split and delayed-label correctness; no future leakage or same-batch validation.
- Exact model/optimizer/replay restoration in deterministic execution mode.
- Reject stale timeline/schema/catalog results; restore cannot learn from the abandoned future.
- Nonfinite gradients, resource exhaustion, divergence, and incompatible checkpoints retain a working baseline/last accepted model.
- Protections, conservation, compatibility, and solvency hold even for adversarial model outputs.
- At least five fixed evaluation seeds for R1 learning evidence, including held-out environmental variation. Publish per-seed metrics, not only the favorable average.
- Provisional R1 gate: aggregate normalized prediction error at least 10% below a declared simple baseline on held-out transitions, plus a trace demonstrating learned predictions change a valid action and improve its measured outcome. Fix datasets and baseline before tuning; if this gate proves unsuitable, record evidence and ask before replacing it.
- Do not claim improved whole-shop management until ablation shows it. R5 requires multi-season comparison against the initial caretaker, including profit, mortality, diversity, and resource use, with uncertainty and failure cases.

## 4. Commands, economy, and API

Test duplicate/out-of-order commands, concurrent tabs, stale targets/quotes, negative/nonfinite amounts, insufficient funds/material, unknown schemas, queue limits, reconnect/resync, and origin/authentication checks. The same target cannot be sold twice; purchased material cannot appear without a debit.

Exercise request-epoch rotation with delayed retries and pending execution; expired commands must never become fresh mutations. Verify pause can always resume even with a full horticultural queue. Restart after acknowledged-but-unsaved actions must force timeline resync without replaying abandoned commands.

Adversarial companion proposals use the identical validation path. Explicit pause, speed change, shutdown, and restore are tested during pending commands and training. Demand supply/budget bounds rule out unlimited artificial arbitrage; a multi-cycle buy/sell test searches for risk-free price exploits caused by implementation errors.

## 5. Persistence and operations

Inject failure after each atomic-save protocol phase: interrupted array writes, manifest rename, database commit, cleanup. Recover either the old or new whole generation, never a mixed one. Test disk-full behavior, invalid paths, malicious archive metadata, corruption, old/new schemas, migration rollback, missing model files, and a second server opening the same data directory.

Verify export/import on a clean supported environment, with learned behavior continued and no copied authentication secrets. Save/reload tests compare biological state, economy, pending events, and learner progression, not only counts.

Launcher gates: fresh locked setup, repeat start without unnecessary install/build, offline restart, changed frontend rebuild, interrupted build recovery, arbitrary working directory, path with spaces, configured port/data directory, missing credential behavior, signal forwarding, and graceful shutdown save.

## 6. UI and mobile acceptance

Automated browser flows cover login, select/inspect, water/fertilize, purchase/sale, protect plant, companion settings, pause/resume, save/export/restore, and disconnect/reconnect. Each release adds its advertised controls. No disabled promised controls or console errors.

At 360 CSS-pixel width: primary actions visible and usable without hover/horizontal page scrolling; touch hit areas at least 44 CSS pixels; pinch/pan do not accidentally mutate plants. Keyboard focus and reduced-motion behavior need checks. Emulation does not prove physical-phone performance: record at least one real touch-device smoke test before claiming mobile validation; ask the user for evidence if no device is accessible.

## 7. Performance and soak gates

Provisional targets, measured on the inspected host with package versions, thread settings, dataset, organ counts, environmental zones, active clients, model configuration, and competing load recorded:

| Metric | Target |
| --- | --- |
| R1 normal tick at 500 plants, default speed | p95 ≤250 ms, p99 ≤1 s |
| R6 normal tick at 1,000 plants, default speed | p95 ≤250 ms, p99 ≤1 s |
| Total server process-tree RSS including learner | steady state ≤1.5 GiB; save/training peak ≤2 GiB |
| Idle connected LAN command admission | p95 ≤200 ms excluding network RTT; execution next eligible tick |
| Default-speed command execution | normally within 6.25 real seconds plus processing; UI shows queued state |
| Browser overview | target ≥30 fps on a named tested midrange mobile device with declared visual settings |
| Save | target ≤5 real seconds, bounded tick impact; no corrupt generation under interruption |
| Training | average ≤10% total host CPU capacity over five-minute windows |

R1 also characterizes 1,000 plants and records bottlenecks; it may not claim the R6 scale gate passed without evidence. Include varied mature organ counts and overlapping canopies, not 1,000 trivial seedlings. Browser memory and local browser+iGPU pressure are reported separately. No unsupported fixed RAM guarantee is inferred from array size alone.

Run at least 24 real hours with learning, autosaves, manager, and client disconnects for each first release of those pathways. Headless accelerated suites cover at least ten simulated years, preserving the same biological timestep and caretaker cadence. Track memory growth, conservation residuals, impossible states, stalled events, exceptions, plant survival, and cash/material ledgers. Zero growth in a bounded population/replay scenario is the memory stability goal; explain retained-history growth separately.

If performance misses a target, profile first. Do not reduce biological activity for offscreen plants or quietly loosen gates. Record the trade-off and consult the user when requirements cannot jointly be met.

## 8. Evidence records

Each release adds `docs/evidence/<release>.md` with exact commands, versions, platform, scenario seeds, input hashes, duration, metrics, failures, corrections, remaining limitations, and artifact locations. Keep large generated results outside Git; commit compact summaries and reproducible scenario definitions. A passing suite demonstrates scoped properties, never absolute bug-freedom.

Documentation-only work checks local links, decision/roadmap consistency, status claims, whitespace, secret/generated-artifact scope, and Git delivery. It does not require installing the application stack or creating cosmetic-only tests.
