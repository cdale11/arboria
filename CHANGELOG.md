# Changelog

## 2026-09-14 — R1 UI audit and upgrade specification

### Changed

- Added the ordered UI-01 through UI-10 plan in `docs/r1-ui-upgrade.md`.
- Added reviewable UI-01 desktop/phone frames, care states, shop/saves/companion
  states, and draft visual tokens in `docs/ui-design-frames.md`.
- Recorded user approval of the UI-01 frames and interaction direction.
- Reopened the broad R1 UI roadmap claim and recorded the four confirmed UI decisions.

### Limitations

- Documentation and scope correction only; no runtime behavior or test result changed.

Records delivered work and actual evidence. Planned features belong in [ROADMAP.md](ROADMAP.md), not in claims of implemented behavior.

## 2026-09-14 — Baseline caretaker companion

### Added

- Added a deterministic baseline caretaker policy that prioritizes low-water
  plants and proposes bounded `nursery.water` actions.
- Added authenticated companion status, settings, and run endpoints. Companion
  commands are submitted through the ordinary command service with
  `actor="companion"`; protections and resource validators remain authoritative.
- Added live UI controls to enable/disable the caretaker and request a care
  check, with an explanation of the latest decision.

### Limitations

- This is the roadmap's baseline caretaker slice, not the neural predictor or
  preference learner. Full authority across all available actions, persisted
  companion policy, learner state, holdout, and ablation evidence remain open.

## 2026-09-14 — Player-facing water and nursery dashboard

### Changed

- Replaced technical water labels with player-facing volume labels: 20 mL for
  per-plant care, 500 mL for shop water, and mL/L in plant/tank displays.
- Added a compact nursery dashboard for cash, tank volume, living plants, and
  nursery time, plus structured plant action cards.

### Evidence and verification

- `npm --prefix web run check`, 23 frontend tests, e2e, and production build
  passed alongside the 154-test Python suite, Ruff, and mypy.

## 2026-09-14 — Isometric 2.5D nursery scene

### Changed

- Reworked the generated nursery SVG from a flat side-view into a clearer 2.5D isometric composition with a diamond floor, row guides, depth-positioned pots, shadows, tilted stems, and layered canopy ellipses.
- Kept the scene display-only: all sizes, stress colors, death opacity, and protection styling still come from server plant projections, and gameplay does not read rendering state.

### Evidence and verification

- `npm --prefix web run check`
- `npm --prefix web run test`: 21 passed.
- `npm --prefix web run test:e2e`: 1 passed.
- `npm --prefix web run build`
- `python -m pytest tests/performance -m performance`: 7 passed in 126.35 seconds.
- 500-plant p95 single-tick latency measured at 60.3 ms; 1,000-plant p95
  measured at 175.3 ms on the inspected host, both below the provisional
  250-ms target.
- The full 500-plant, 10-sim-year run completed in 853.22 seconds with finite
  state, valid water capacity, 42.56 MiB peak RSS, approximately `1e-12 kg`
  water residual, zero exceptions, and no stall. The 24-real-hour operational
  soak remains open.
- Added the marked headless scale/soak harness under `tests/performance/` and
  included it in strict mypy coverage.

### Performance correction

- Removed redundant whole-organ topology validation and repeated full-list
  exchange/assimilation scans from private hot-loop helpers. Public
  `advance_nursery` boundary validation remains in place; this reduced the
  profiled 500-plant tick from approximately 2.06 s to 0.056 s without
  disabling biological activity.

## 2026-09-14 — Nursery UI presentation pass

### Changed

- Added a framed living-nursery presentation with responsive plant cards,
  grouped controls, status styling, and narrow-screen layout improvements.
- Kept all controls and behavior within the existing R1 inspection, care, shop,
  save, clock, and protection scope.
- Unified live status and plant-card formatting: cash now consistently shows as
  dollars, short lengths as centimetres, small masses as grams, and species IDs
  as readable names instead of exposing raw minor units or scientific notation.
- Frontend verification: `npm --prefix web run check`, 21 frontend tests,
  e2e, and production build passed.

## 2026-09-14 — Live 2.5D nursery scene wiring

### Fixed

- Mounted the generated 2.5D nursery SVG in the live frontend app refresh path so it is visible in the browser, not only in the standalone render helper.
- Added visible-width SVG styling and a mounted-app regression test for the scene.

### Evidence and verification

- `npm --prefix web run check`
- `npm --prefix web run test`: 21 passed.
- `npm --prefix web run test:e2e`: 1 passed.
- `npm --prefix web run build`
- `python -m pytest tests/unit/app/test_nursery_api.py tests/unit/app/test_shop_api.py`: 18 passed, with the known FastAPI/Starlette `TestClient` deprecation warning.

## 2026-09-14 — R1 aggregate evidence synchronization

### Added

- Added `docs/evidence/R1.md` aggregating implemented R1 foundation coverage, current gate results, evidence files, and open release blockers.
- Updated roadmap status for completed non-AI biology, documentation, unit/static check, and launcher gate items.
- Corrected README backup language to distinguish implemented current-domain export/import from unimplemented learner-inclusive saves.

### Evidence and verification

- Documentation/status change prepared after the passing full gate run recorded in `docs/evidence/R1.md`.

### Limitations

- Full R1 release remains blocked by open AI/ML, physical touch-device, and performance/soak gates.

## 2026-09-14 — Baseline caretaker companion implementation

### Added

- Added `docs/evidence/R1-companion.md` documenting the baseline caretaker
  slice and its explicit limits.
- Added deterministic low-water caretaker policy, authenticated companion
  status/settings/run endpoints, companion-owned validated watering receipts,
  and live enable/check controls.
- Added policy, API, and frontend regression coverage.

### Limitations

- The full-authority caretaker and neural prediction/preference learner roadmap
  items remain open; this change is the first honest baseline companion slice.

## 2026-09-14 — R1 generated nursery view and current-domain backups

### Added

- Added a generated SVG nursery scene that projects plant size, stress, alive/dead state, and protection state without affecting simulation or command validation.
- Added dependency-free current-domain export/import through `/api/v1/saves/export` and `/api/v1/saves/import` using bounded base64 zip archives.
- Added save UI controls for export/import archives and expanded e2e coverage across backup controls.
- Added checkpoint archive tests for round-trip validation, extra-entry rejection, invalid-base64 API rejection, and restore from imported protected plant state.

### Evidence and verification

- Targeted during implementation: `python -m pytest tests/unit/app/test_checkpoints.py tests/unit/app/test_shop_api.py` passed with 21 tests.
- Targeted during implementation: `mypy src tests/unit`, `ruff check ...`, `npm --prefix web run check`, `npm --prefix web run test`, and `npm --prefix web run test:e2e` passed.

### Limitations

- Export/import covers the implemented current domains only. Learner arrays, optimizer, replay, RNG streams, and companion policy state remain unsupported because those systems are not implemented.
- The generated SVG is a projection, not a full art/rendering engine or performance-validated mobile renderer.

## 2026-09-14 — R1 launcher gates and protected touch controls

### Added

- Added `ARBORIA_LAUNCHER_CHECK=1` for setup/build/fingerprint launcher checks that exit without starting Uvicorn.
- Added launcher gate tests for invalid ports, arbitrary working directories, path-with-spaces roots, stale frontend fingerprint rebuilds, and repeat checks without unnecessary rebuilds.
- Added persisted plant protection with `nursery.protect` and `nursery.unprotect`; protected plants are exposed in projections and rejected by sale validation until unprotected.
- Added browser controls for protect/unprotect and responsive 44 CSS-pixel minimum touch targets at narrow widths.
- Replaced the placeholder e2e script with a real locked Vitest/jsdom full-flow control test.

### Evidence and verification

- `python -m pytest tests/unit/app/test_shop_api.py tests/unit/app/test_launcher.py` passed with 15 tests.
- `npm --prefix web run test` passed with 18 tests.
- `npm --prefix web run test:e2e` passed with 1 test.

### Limitations

- Browser e2e uses locked Vitest/jsdom, not native browser binaries. No physical touch-device smoke, native browser automation, companion settings, export/import, fertilizer flow, or procedural 2.5D rendering is claimed.

## 2026-09-14 — R1 stream resync and revisioned deltas

### Added

- Added JSON-parsed stream `sync {base_revision}` handling with current-state `synced` responses and stale-state authoritative replacement snapshots.
- Added revisioned `delta` frames for ping-driven biological advancement; deltas include clock/loop/nursery projections and `base_revision` from the prior revision.
- Updated stream architecture and baseline evidence to distinguish implemented ephemeral full-projection deltas from unimplemented persistent replay.

### Evidence and verification

- `python -m pytest tests/unit/app/test_server.py` passed with 38 tests.
- `python -m pytest tests/unit` passed with 141 tests.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed with 16 tests.
- `npm --prefix web run build` passed.

### Limitations

- R1 stream deltas are ephemeral full-projection deltas; no persistent replay log, outbound subscriber queue implementation, detailed inspection subscription, or frontend WebSocket consumer exists yet.

## 2026-09-14 — R1 crash recovery, migration, and atomic saves

### Added

- Added startup recovery: corrupt or missing active checkpoints fall back along the manifest parent chain, or boot starter state with the active record cleared, with warning logs.
- Added versioned nursery migration covering schema versions 1–4 with starter fallbacks; newer stamps are rejected.
- Added atomic-save failure-injection, fallback-chain, migration, and read-only-directory tests.
- Updated validation evidence and persistence notes for the new recovery behavior.

### Evidence and verification

- `python -m pytest tests/unit` passed with 138 tests.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed with 16 tests.
- `npm --prefix web run build` passed.

### Limitations

- Recovery baseline only: corrupt generations are skipped, never repaired; no repair tooling, import validation, learner/RNG recovery, export/import, or retention exists yet. A read-only data directory still fails saves with HTTP 500 rather than a queued retry.

## 2026-09-14 — R1 lifecycle controls while paused

### Added

- Locked paused-world lifecycle behavior with sequence tests: frozen ticks with live commands, paused save/restore/speed/resume, and paused restart recovery.
- Verified live SIGTERM shutdown while paused persists clock state and checkpoints; shutdown stays process-signal driven with no new endpoint.

### Evidence and verification

- `python -m pytest tests/unit` passed with 131 tests.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed with 16 tests.
- `npm --prefix web run build` passed.

### Limitations

- Lifecycle baseline only: horticultural commands apply immediately against a frozen tick rather than queueing while paused, there is no shutdown API endpoint, and no crash/disk-failure recovery, migration protocol, or failure-injection tests exist yet.

## 2026-09-14 — R1 desktop nursery controls

### Added

- Mounted an interactive browser nursery: per-plant inspect/water/sell, shop buy-water/buy-plant with species selection, clock pause/resume/speed, checkpoint/named-save/restore/refresh, organ detail panel, and receipt/error status reporting.
- Added a strict API client with CSRF headers, per-command world snapshot refresh, and response-shape validation.
- Added controls contract documentation and evidence.

### Evidence and verification

- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed with 16 tests.
- `npm --prefix web run build` passed.
- `python -m pytest tests/unit` passed with 128 tests.

### Limitations

- Desktop controls only: no touch-target or small-screen review, no plant protection controls, no procedural 2.5D rendering, no fertilizer flows, no companion settings, and no export exists yet.

## 2026-09-14 — R1 shop economy baseline

### Added

- Added integer-minor-unit cash economy with starting funds, provisional price table, and finite per-species buyer demand.
- Added `shop.buy_water` reservoir refills with a 5.0 kg reservoir cap.
- Added `shop.buy_plant` purchases that add live starter plants with fresh IDs, zones, and species mapping.
- Added `shop.sell_plant` demand-limited sales that remove live plants; dead, unknown, and already-sold plants are rejected.
- Persisted species mapping and economy state in checkpoint schema 4 with restore/startup fallback.
- Exposed cash and demand in projections, summaries, stream snapshots, and UI.
- Added kernel, inventory, API, duplicate-command, demand, anti-arbitrage, and persistence tests.
- Added economy contract documentation and evidence.

### Evidence and verification

- `python -m pytest tests/unit` passed with 128 tests.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed with 5 tests.
- `npm --prefix web run build` passed.

### Limitations

- Shop baseline only: no fertilizer or amendment items, no seed/fruit/cutting products, no shop UI buttons (actions via API), no price forecasting, no supplier limits beyond demand counts, no species calibration, and no companion exists yet. All prices are provisional gameplay parameters, not market data.

## 2026-09-14 — R1 species catalog baseline

### Added

- Added six-species catalog with greenhouse/outdoor sites and explicitly provisional parameters.
- Parameterized nursery ticks by species: assimilation, water, nutrient, growth, damage coefficients, and site PAR.
- Starter plant 1 grows greenhouse basil; starter plant 2 grows outdoor oak; starter root N/P/K matches species references.
- Exposed species/site in projections, summaries, stream snapshots, and UI.
- Added catalog validation tests and six reviewed 200-tick watered reference scenarios.
- Added species catalog documentation with per-species supported/approximated/unsupported coverage.

### Evidence and verification

- `python -m pytest tests/unit` passed with 106 tests.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed with 5 tests.
- `npm --prefix web run build` passed.

### Limitations

- Species baseline only: shared starter geometry with no morphology grammar, no measured species constants, CAM approximated with the C3 response, no fertilizer input, no reproduction, dormancy, pruning response, economy, or companion exists yet.

## 2026-09-14 — R1 nutrient stress, damage, and death baseline

### Added

- Added pure N/P/K kernel with bounded substrate uptake, Liebig-minimum deficiency stress, irreversible damage, and death.
- Gave each starter plant finite substrate N/P/K with no fertilizer input; live nutrient stress feeds assimilation.
- Combined water/nutrient stress below 0.5 accrues organ damage; dead plants stop ticking.
- Persisted nutrient zones in checkpoints (schema version 3) with restore/startup fallback to starter values.
- Exposed alive/damage/nutrient state in plant projections, detail endpoint, summaries, and UI.
- Added kernel, starvation-death, depletion, payload, API, and persistence tests.
- Updated roadmap, README, biology notes, and evidence documentation.

### Evidence and verification

- `python -m pytest tests/unit` passed with 96 tests.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed with 5 tests.
- `npm --prefix web run build` passed.

### Limitations

- Nutrient baseline only: no fertilizer input, layered substrate, waterlogging, damage recovery, rainfall/VPD coupling, species calibration, economy, companion, irrigation automation, export/import, or retention exists yet. All nutrient parameters are provisional, not measured species constants.

## 2026-09-14 — R1 nursery-water baseline

### Added

- Added pure bounded root-zone water kernel with uptake, transpiration, drainage, and stress.
- Coupled per-plant assimilation water factor to live zone fullness.
- Added per-plant 0.20 kg zones, finite 2.0 kg reservoir, and receipt-backed `nursery.water` command.
- Persisted zones/reservoir in checkpoints with restore/startup recovery.
- Exposed zone water/stress in plant projections and UI totals.
- Added kernel, tick, watering, API, and persistence tests.
- Updated roadmap, README, biology/persistence/architecture notes, and evidence documentation.

### Evidence and verification

- `python -m pytest tests/unit` passed with 87 tests.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed with 5 tests.
- `npm --prefix web run build` passed.
- Fixed the served page rendering only the dependency-baseline fallback: the frontend bootstrap now fetches `/api/v1/world` and `/api/v1/plants` and renders live nursery projections with honest fetch-failure messaging.
- Live smoke test verified authenticated `/api/v1/plants` returns the starter nursery and authenticated `/` serves the rebuilt bundle containing the nursery loader.

### Limitations

- Water baseline only: no nutrient uptake/chemistry, layered substrate, waterlogging, rainfall/VPD coupling, stress damage, death, species calibration, economy, companion, irrigation automation, queued resume-time care scheduler, export/import, or retention exists yet.

## 2026-09-14 — R1 living-nursery baseline

### Added

- Added pure deterministic starter nursery with two root/stem/leaf-cohort plants.
- Wired bounded carbon assimilation and resource-bounded stem growth into world ticks.
- Added authenticated `/api/v1/plants` and `/api/v1/plants/{id}` inspection projections.
- Added nursery summaries to world status and stream snapshots.
- Added nursery biology to checkpoint state with restore and startup recovery.
- Added minimal frontend nursery inspection rendering with honest limitations.
- Added backend and persistence tests for tick growth, plant APIs, checkpoints, and restore.
- Updated roadmap, README, biology/architecture-adjacent docs, and evidence documentation.

### Evidence and verification

- `python -m pytest tests/unit` passed with 80 tests.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed.
- `npm --prefix web run build` passed.

### Limitations

- Living-nursery baseline only: no water/nutrient uptake, root-zone environment, stress, damage, death, species catalog, economy, companion, reconnect deltas, procedural 2.5D rendering, touch controls, planting/care/sales actions, export/import, or calibration exists yet.

## 2026-09-12 — P0 planning baseline

### Added

- Confirmed design choices for organ-level biology, accelerated continuous time, mixed nursery, 2.5D presentation, 500–1,000-plant target, strict consequences, full-authority companion, staged emergence, single-shop password access, and complete learner persistence.
- Adopted default calendar of one simulated day per 30 real minutes; restart resumes saved simulation time without downtime catch-up.
- Defined Python/TypeScript architecture, one-writer tick order, compact organ arrays, validated command protocol, environment-local dependency policy, and single-script setup/build/start contract.
- Defined biological units, resource-accounting rules, functional–structural growth, physiological approximations, species provenance, and later reproduction/bonsai/ecology contracts.
- Specified small online neural ensembles, preference learning, bounded training, model evaluation/activation, baseline fallback, and restricted experimental rule invention.
- Specified consistent world/learner checkpoint generations, restore timeline isolation, export/import, migrations, crash/disk-failure recovery, and authentication boundaries.
- Established dependency-ordered complete releases, test matrices, provisional performance budgets, scientific evidence requirements, and mobile validation gates.
- Added mandatory agent SOP and an incident log recording two actual initial-inspection mistakes.

### Evidence and verification

- Repository inspection found an empty `main` branch with no existing commits or application files, and configured `origin` at `git@github.com:cdale11/arboria.git`.
- Host inspection using `lscpu`, `free -h`, `lspci`, and `conda list` established Ryzen 3 8300GE (4 cores / 8 threads), AMD integrated graphics, approximately 6.9 GiB usable RAM, and existing `arboria` with Python 3.14.7. These are observations, not benchmark results.
- User decisions were collected through the question tool; adopted defaults and release gates are separated in `docs/decisions.md`.
- Documentation checker passed for all 12 Markdown files, including 16 local link destinations, required document presence, balanced fenced code blocks, and trailing whitespace. The check used Python's standard library inside activated `arboria`, without installing dependencies.
- `git diff --check` passed. Roadmap/status consistency and intended-file scope were reviewed; Git delivery verification is reported with the final commit result.

### Limitations

- Documentation only: no simulation, launcher, dependency locks, package installation, trained models, application tests, browser checks, or runtime benchmarks were delivered.
- Python 3.14 compatibility with the proposed numerical stack remains unverified; R1 must resolve it.
- Biological equations are modeling contracts; species coefficients have not been sourced or scientifically calibrated.
- Performance budgets and learning improvement thresholds are provisional acceptance targets, not achieved measurements.
- No project-wide software license has been selected.

## 2026-09-12 — R1 dependency baseline

### Added

- Added `environment.yml` with direct Conda requirements for Python 3.13, NumPy, Numba, FastAPI, Uvicorn, pytest, Hypothesis, mypy, Ruff, and Node.js.
- Added `conda-linux-64.lock`, generated from the installed `arboria` environment with `conda list --explicit`.
- Added `web/package.json` and `web/package-lock.json` with pinned TypeScript, Vite, Three.js, Vitest, jsdom, and type dependencies.
- Added minimal frontend smoke files so the locked TypeScript/Vite/Vitest toolchain can be verified without claiming gameplay exists.
- Added `pyproject.toml` for initial Python lint/type/test configuration and `.gitignore` for runtime state, credentials, caches, frontend builds, and `node_modules`.
- Added `docs/dependencies.md` and `docs/evidence/R1-dependencies.md` documenting dependency policy, commands, evidence, and limitations.
- Updated `README.md`, `ROADMAP.md`, architecture decisions, and `MISTAKES.md` for the dependency baseline.

### Evidence and verification

- Conda dry run resolved the direct stack from allowed default channels without pip or system packages.
- Conda install completed, moving `arboria` from Python 3.14.7 to Python 3.13.15 to satisfy the numerical/server/test stack.
- npm lock/install were rerun with `PATH="$CONDA_PREFIX/bin:$PATH"`, verifying Conda Node `v26.5.1` and npm `11.17.0`.
- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed with 1 Vitest/jsdom smoke test.
- `npm --prefix web run build` passed with Vite 7.1.7.
- Python smoke imported NumPy 2.4.6, Numba 0.66.0, FastAPI 0.138.0, Uvicorn 0.52.4, pytest 9.0.3, and Hypothesis 6.165.10; a trivial Numba `njit` function compiled and ran.
- `ruff check .` passed.

### Limitations

- Dependency baseline only: no game server, launcher, simulation, persistence, economy, companion logic, real UI, or application test suite exists yet.
- Browser e2e tooling is intentionally not selected yet; `web/package.json` keeps `test:e2e` failing until a real suite is added.
- npm warned that `esbuild` has an install script not covered by npm's `allowScripts` review flow. The current build passes, but launcher/setup work must choose an explicit policy.
- Locks are Linux x86-64/local-browser-stack focused; cross-platform support is not claimed.

## 2026-09-12 — R1 launcher/server baseline

### Added

- Added `run.sh`, a baseline single-command launcher that discovers Conda, activates `arboria`, prioritizes Conda Node/npm, builds browser assets when source/config fingerprints change, and starts Uvicorn.
- Added a minimal FastAPI application with `/health`, `/api/v1/health`, and static frontend serving for the current baseline page.
- Added unit tests for health endpoint scope and API/plain health consistency.
- Updated README, roadmap, architecture notes, and evidence documentation to reflect the current runnable baseline without claiming gameplay exists.

### Evidence and verification

- `python -m pytest tests/unit` passed.
- pytest emitted a `StarletteDeprecationWarning` from FastAPI's re-exported `TestClient`; it did not fail the suite.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed.
- `npm --prefix web run build` passed.
- A smoke run of `ARBORIA_PORT=8766 ./run.sh` served `/health` successfully and reported unimplemented authentication, simulation, persistence, and companion systems.

### Limitations

- Launcher/server baseline only: authentication, world ownership, persistence, simulation, economy, companion, e2e browser testing, offline repeat-start evidence, process lock, and failure-injection gates remain incomplete.

## 2026-09-13 — R1 authentication baseline

### Added

- Added shared-password setup integrated into `run.sh`, with interactive first-run prompts or controlled noninteractive `ARBORIA_SETUP_PASSWORD` setup.
- Added local PBKDF2-HMAC-SHA256 password hashing, hashed session-token storage, HttpOnly SameSite session cookies, auth status/login/logout endpoints, and protected root-page behavior.
- Added auth-focused unit tests using isolated temporary data directories.
- Updated README, roadmap, architecture notes, and evidence documentation to reflect baseline authentication without claiming the world simulation exists.

### Evidence and verification

- `python -m pytest tests/unit` passed with 6 tests and the documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed.
- `npm --prefix web run build` passed.
- A smoke run of `ARBORIA_HOST=127.0.0.1 ARBORIA_PORT=8767 ARBORIA_DATA_DIR=<tmp> ARBORIA_SETUP_PASSWORD=<temporary> ./run.sh` configured a password, served `/health`, and did not store the plaintext password.

### Limitations

- Authentication baseline only: CSRF/origin hardening, login rate limiting, Secure-cookie HTTPS behavior, process lock, world ownership, command authorization, persistence, simulation, economy, companion, and e2e browser testing remain incomplete.

## 2026-09-13 — R1 authentication hardening

### Added

- Added session-bound CSRF tokens with readable SameSite CSRF cookies and required `X-Arboria-CSRF` headers for authenticated logout.
- Added same-origin rejection for unsafe HTTP requests with mismatched `Origin` or `Referer` headers.
- Added in-memory failed-login throttling after five failures from one client address in a 15-minute window.
- Expanded auth tests for CSRF-protected logout, cross-origin rejection, and rate limiting.
- Updated README, roadmap, architecture notes, and evidence documentation.

### Evidence and verification

- `python -m pytest tests/unit` passed with 8 tests and the documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed.
- `npm --prefix web run build` passed.
- A smoke run of `ARBORIA_HOST=127.0.0.1 ARBORIA_PORT=8767 ARBORIA_DATA_DIR=<tmp> ARBORIA_SETUP_PASSWORD=<temporary> ./run.sh` configured a password and served `/health` with authentication marked implemented.

### Limitations

- Hardening baseline only: rate limiting is in-memory, Secure-cookie HTTPS behavior is not active on LAN HTTP, command/WebSocket authorization does not exist yet, and world ownership/process lock/persistence/simulation remain incomplete.

## 2026-09-13 — R1 process-lock baseline

### Added

- Added `DataDirectoryLock`, an OS `flock`-backed exclusive lock on `server.lock` under `ARBORIA_DATA_DIR`.
- Integrated the process lock with FastAPI lifespan startup/shutdown so a second server using the same data directory fails instead of creating another owner.
- Added process-lock unit tests for second-owner rejection and release/reacquire behavior.
- Updated health status, README, roadmap, architecture notes, and evidence documentation.

### Evidence and verification

- `python -m pytest tests/unit` passed with 10 tests and the documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed.
- `npm --prefix web run build` passed.
- A two-process smoke check started `./run.sh` with one temporary data directory, verified the first server served `/health`, and verified a second server with the same data directory failed instead of serving concurrently.

### Limitations

- Process-lock baseline only: no SQLite persistence, checkpointing, migration, save/restore, world tick loop, economy, companion, or command streaming exists yet.

## 2026-09-13 — R1 simulation-clock baseline

### Added

- Added `SimulationClock`, an in-memory server-owned clock with default 48x speed, pause/resume, speed validation, and calendar-derived status fields.
- Added authenticated `/api/v1/clock` status endpoint and CSRF-protected pause/resume/speed endpoints.
- Added deterministic clock unit tests and API tests for auth/CSRF/speed behavior.
- Updated README, roadmap, health status, and evidence documentation.

### Evidence and verification

- `python -m pytest tests/unit` passed with 17 tests and the documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed.
- `npm --prefix web run build` passed.
- A smoke run of `ARBORIA_HOST=127.0.0.1 ARBORIA_PORT=8767 ARBORIA_DATA_DIR=<tmp> ARBORIA_SETUP_PASSWORD=<temporary> ./run.sh` served `/health` with phase `r1-clock-baseline` and `simulation_clock: true`.

### Limitations

- Clock baseline only: state is not persisted, no biological tick loop consumes it, no command queue exists, and no frontend clock controls exist yet.

## 2026-09-13 — R1 roadmap granularity update

### Changed

- Split the R1 roadmap scope into finer evidence-backed checkbox groups so completed baseline slices are visibly checked while unfinished parts remain unchecked.

### Evidence and verification

- Documentation-only change; Markdown link/fence/whitespace checks and `git diff --check` were run.

### Limitations

- No implementation behavior changed.

## 2026-09-13 — Full roadmap granularity update

### Changed

- Split R2 through R7 into grouped granular checklist items matching the R1 roadmap style.
- Preserved all later-release items as unchecked because no R2-R7 implementation evidence exists yet.

### Evidence and verification

- Documentation-only change; Markdown link/fence/whitespace checks and `git diff --check` were run.

### Limitations

- No implementation behavior changed.

## 2026-09-13 — R1 world-metadata baseline

### Added

- Added `MetadataStore`, a SQLite metadata baseline for one local world under `ARBORIA_DATA_DIR/world.sqlite3`.
- Persisted world UUID, fresh process-start timeline UUID, schema version, and simulation clock state.
- Added authenticated `/api/v1/world` status endpoint.
- Updated clock startup/shutdown and clock routes so restart resumes saved clock state without wall-clock catch-up.
- Added unit tests for metadata creation, timeline rotation, durable SQLite settings, clock state persistence, and server restart behavior.
- Updated README, roadmap, persistence documentation, and evidence documentation.

### Evidence and verification

- `python -m pytest tests/unit/app/test_metadata.py tests/unit/app/test_server.py tests/unit/sim/test_clock.py` passed with 20 tests and the documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check src/arboria/app/metadata.py src/arboria/app/server.py src/arboria/sim/clock.py tests/unit/app/test_metadata.py tests/unit/app/test_server.py tests/unit/sim/test_clock.py` passed.
- `mypy src tests/unit` passed.

### Limitations

- Metadata persistence only: immutable checkpoints, autosave, named saves, restore, export/import, command receipts, migrations, biological state, and the world tick loop remain unimplemented.

## 2026-09-13 — R1 command-envelope baseline

### Added

- Added bounded command envelope parsing and validation for schema version, UUIDs, request epoch, kind, payload size/depth/type, and nonfinite numbers.
- Added persisted command receipts in SQLite, keyed by timeline, request epoch, and command ID, with duplicate submissions returning the original receipt.
- Added request epoch metadata that increments on process restart.
- Added authenticated, CSRF-protected `/api/v1/commands` endpoint.
- Routed existing clock pause/resume/set-speed actions through the command endpoint as the first real command handlers.
- Added tests for envelope rejection, receipt persistence, deduplication, stale epoch rejection, and clock-command application.
- Updated README, roadmap, architecture notes, and evidence documentation.

### Evidence and verification

- `python -m pytest tests/unit/app/test_commands.py tests/unit/app/test_metadata.py tests/unit/app/test_server.py` passed with 22 tests and the documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check src/arboria/app/commands.py src/arboria/app/metadata.py src/arboria/app/server.py tests/unit/app/test_commands.py tests/unit/app/test_metadata.py tests/unit/app/test_server.py` passed.
- `mypy src tests/unit` passed.

### Limitations

- Command baseline only: no horticultural command kinds, biological tick queue, WebSocket notifications, receipt expiry policy, checkpoint reconciliation, or save/restore behavior exists yet.

## 2026-09-13 — R1 stream baseline

### Added

- Added authenticated `/api/v1/stream` WebSocket endpoint with same-origin upgrade checks.
- Added initial world/clock snapshot messages carrying schema version, world/timeline identity, revision fields, request epoch, and clock status.
- Added bounded inbound message handling with ping/pong support and oversized-message rejection.
- Added stream API tests for authentication, cross-origin rejection, snapshot contents, ping/pong, and message size limits.
- Updated health status, README, roadmap, architecture notes, and evidence documentation.

### Evidence and verification

- `python -m pytest tests/unit/app/test_server.py` passed with 19 tests and the documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check src/arboria/app/server.py tests/unit/app/test_server.py` passed.
- `mypy src tests/unit` passed.

### Limitations

- Stream baseline only: no biological projections, revisioned deltas, reconnect replay, resync recovery, frontend stream consumption, or outbound subscriber queues exist yet.

## 2026-09-13 — R1 world-loop baseline

### Added

- Added `WorldLoop`, a single in-process accumulator that consumes clock state into fixed 300-sim-second ticks and world revisions.
- Persisted `sim_tick`, `world_revision`, and consumed simulation time in SQLite metadata.
- Exposed tick/revision fields through `/api/v1/world` and stream snapshots.
- Added deterministic loop tests and metadata/server coverage for persisted tick state and API exposure.
- Updated README, roadmap, architecture notes, persistence notes, and evidence documentation.

### Evidence and verification

- `python -m pytest tests/unit/sim/test_world_loop.py tests/unit/app/test_metadata.py tests/unit/app/test_server.py` passed with 28 tests and the documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check src/arboria/sim/world_loop.py src/arboria/app/metadata.py src/arboria/app/server.py tests/unit/sim/test_world_loop.py tests/unit/app/test_metadata.py tests/unit/app/test_server.py` passed.
- `mypy src tests/unit` passed.

### Limitations

- World-loop baseline only: ticks do not run biological kernels, event processing, manager planning, horticultural command execution, projection deltas, or checkpoint scheduling yet.

## 2026-09-13 — R1 checkpoint-layout baseline

### Added

- Added immutable metadata-only checkpoint generation directories under `checkpoints/<checkpoint_id>/`.
- Added checkpoint `manifest.json` and `state.json` writing with SHA-256 file metadata and directory fsyncs before final promotion.
- Added SQLite checkpoint registration and active checkpoint ID updates.
- Added authenticated, CSRF-protected `/api/v1/saves/checkpoint` manual save endpoint.
- Added tests for checkpoint file layout, hashes, active checkpoint updates, and API auth/CSRF behavior.
- Updated health status, README, roadmap, persistence notes, and evidence documentation.

### Evidence and verification

- `python -m pytest tests/unit/app/test_checkpoints.py tests/unit/app/test_metadata.py tests/unit/app/test_server.py` passed with 30 tests and the documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check src/arboria/app/checkpoints.py src/arboria/app/metadata.py src/arboria/app/server.py tests/unit/app/test_checkpoints.py tests/unit/app/test_metadata.py tests/unit/app/test_server.py` passed.
- `mypy src tests/unit` passed.

### Limitations

- Checkpoint-layout baseline only: no biology, economy, learner state, pending queues, autosave, named saves, restore, export/import, retention, corruption recovery, or failure-injection tests exist yet.

## 2026-09-13 — R1 named-saves baseline

### Added

- Added SQLite `snapshot_names` records for metadata-only named saves.
- Added authenticated `/api/v1/saves` listing endpoint.
- Added CSRF-protected `/api/v1/saves/named` endpoint that creates a metadata-only checkpoint and assigns a protected name.
- Added bounded save-name validation rejecting empty, overly long, and path-like names.
- Added metadata/server tests for named snapshot persistence, authentication, CSRF, checkpoint creation, listing, and name validation.
- Updated README, roadmap, persistence notes, and evidence documentation.

### Evidence and verification

- `python -m pytest tests/unit/app/test_metadata.py tests/unit/app/test_server.py` passed with 34 tests and the documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check src/arboria/app/metadata.py src/arboria/app/server.py tests/unit/app/test_metadata.py tests/unit/app/test_server.py` passed.
- `mypy src tests/unit` passed.

### Limitations

- Named-saves baseline only: saves point to metadata-only checkpoints; restore, export/import, autosave, retention, corruption recovery, biology/economy/learner checkpoint contents, and save UI remain unimplemented.

## 2026-09-13 — AI/ML roadmap highlighting

### Changed

- Marked roadmap checklist items requiring AI, ML, neural-network, companion, or manager-learning systems in blue.
- Added a roadmap legend explaining the blue highlight.

### Evidence and verification

- Documentation-only change; Markdown link/fence/whitespace checks and `git diff --check` were run.

### Limitations

- No implementation behavior changed.

## 2026-09-13 — Visible AI/ML roadmap tags

### Changed

- Replaced HTML color-only roadmap markers with literal `[AI/ML]` tags so GitHub Markdown and raw file views show the AI/ML-dependent items clearly.

### Evidence and verification

- Documentation-only change; Markdown link/fence/whitespace checks and `git diff --check` were run.

### Limitations

- No implementation behavior changed.

## 2026-09-13 — R1 metadata-restore baseline

### Added

- Added checkpoint manifest/state validation for metadata-only checkpoint generations.
- Added CSRF-protected `/api/v1/saves/restore` endpoint accepting a checkpoint ID or named save.
- Restored clock and tick/revision state from validated metadata checkpoints.
- Rotated timeline and request epoch on restore, invalidating old command envelopes.
- Added tests for corrupt checkpoint rejection, named-save restore, timeline/epoch rotation, clock restoration, and unknown save names.
- Updated README, roadmap, persistence notes, and evidence documentation.

### Evidence and verification

- `python -m pytest tests/unit/app/test_checkpoints.py tests/unit/app/test_metadata.py tests/unit/app/test_server.py` passed with 38 tests and the documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check src/arboria/app/checkpoints.py src/arboria/app/metadata.py src/arboria/app/server.py tests/unit/app/test_checkpoints.py tests/unit/app/test_metadata.py tests/unit/app/test_server.py` passed.
- `mypy src tests/unit` passed.

### Limitations

- Metadata-restore baseline only: no biology, economy, learner state, RNG streams, pending events, pre-restore safety snapshots, export/import, autosave, retention, UI, or full corruption-recovery flow exists yet.

## 2026-09-13 — R1 metadata-autosave baseline

### Added

- Added metadata-only autosave checkpoint purpose and persisted last autosave timestamp.
- Added checkpoint `purpose` to manifests, state payloads, and SQLite checkpoint records.
- Added autosave status fields to `/api/v1/saves`.
- Triggered due autosaves from authenticated world status checks, using a default 60-second interval and `ARBORIA_AUTOSAVE_INTERVAL_SECONDS` for tests/configuration.
- Added tests for autosave status, due autosave creation, autosave metadata persistence, and checkpoint purpose fields.
- Updated README, roadmap, persistence notes, and evidence documentation.

### Evidence and verification

- `python -m pytest tests/unit/app/test_checkpoints.py tests/unit/app/test_metadata.py tests/unit/app/test_server.py` passed with 41 tests and the documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check src/arboria/app/checkpoints.py src/arboria/app/metadata.py src/arboria/app/server.py tests/unit/app/test_checkpoints.py tests/unit/app/test_metadata.py tests/unit/app/test_server.py` passed.
- `mypy src tests/unit` passed.

### Limitations

- Metadata-autosave baseline only: no background autosave worker, restore safety snapshot, retention policy, export/import, biology/economy/learner state, or UI exists yet.

## 2026-09-13 — R1 interrupted-checkpoint cleanup baseline

### Added

- Added startup cleanup for interrupted metadata-checkpoint generation directories left as hidden `*.tmp` directories under `checkpoints/`.
- Added tests verifying cleanup removes interrupted generation directories while preserving complete checkpoint directories.
- Updated roadmap, persistence notes, and evidence documentation.

### Evidence and verification

- `python -m pytest tests/unit/app/test_checkpoints.py tests/unit/app/test_server.py` passed with 35 tests and the documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check src/arboria/app/checkpoints.py src/arboria/app/server.py tests/unit/app/test_checkpoints.py tests/unit/app/test_server.py` passed.
- `mypy src tests/unit` passed.

### Limitations

- Cleanup baseline only: active-checkpoint corruption handling, disk-full behavior, migration tooling, restore fallback selection, retention, and failure-injection tests remain unimplemented.

## 2026-09-13 — R1 active-checkpoint validation baseline

### Added

- Added startup validation for the recorded active metadata checkpoint.
- Startup now verifies active checkpoint file presence, manifest checkpoint ID, `state.json` size, and SHA-256 hash before admitting clients.
- Added tests proving corrupt active checkpoint state fails startup clearly.
- Updated roadmap, persistence notes, and evidence documentation.

### Evidence and verification

- `python -m pytest tests/unit/app/test_checkpoints.py tests/unit/app/test_server.py` passed with 36 tests and the documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check src/arboria/app/server.py tests/unit/app/test_server.py` passed.
- `mypy src tests/unit` passed.

### Limitations

- Active-checkpoint validation baseline only: fallback selection, repair, import validation, disk-full handling, migrations, and complete biology/economy/learner recovery remain unimplemented.

## 2026-09-13 — R1 organ-topology biology baseline

### Added

- Added pure biology organ topology and resource-pool module.
- Added R1 organ kinds for structural organs and leaf/root cohorts.
- Added explicit structural carbon, reserve carbon, water, nitrogen, phosphorus, and potassium pools.
- Added validation for stable IDs, one root per plant, existing same-plant parents, acyclic parentage, finite nonnegative values, bounded damage, and cohort-count rules.
- Added biology unit tests for topology and resource invariants.
- Updated roadmap, biology docs, and evidence documentation.

### Evidence and verification

- `python -m pytest tests/unit/biology/test_organs.py` passed with 7 tests.
- `ruff check src/arboria/biology tests/unit/biology` passed.
- `mypy src tests/unit` passed.

### Limitations

- Biology baseline only: no growth, light, carbon assimilation, water/nutrient uptake, stress, damage progression, death, species catalog, persistence integration, commands, or UI exists yet.

## 2026-09-13 — R1 vegetative-growth baseline

### Added

- Added pure resource-bounded vegetative growth kernel for existing structural organs.
- Added finite, nonnegative growth demands that target existing root/stem/branch organs only.
- Added limiting-resource scaling across reserve carbon, water, nitrogen, phosphorus, and potassium.
- Added root-pool debits and target-organ resource/length increments without creating new organs.
- Added biology tests for full growth, resource-limited growth, material accounting, invalid targets, and invalid demands.
- Updated roadmap, biology docs, and evidence documentation.

### Evidence and verification

- `python -m pytest tests/unit/biology` passed with 12 tests.
- `ruff check src/arboria/biology tests/unit/biology` passed.
- `mypy src tests/unit` passed.

### Limitations

- Vegetative-growth baseline only: no photosynthesis, root/substrate uptake, light model, nutrient chemistry, organ initiation, stress/damage/death, species grammars, persistence integration, commands, or UI exists yet.

## 2026-09-13 — R1 carbon-assimilation baseline

### Added

- Added pure bounded light-driven carbon assimilation kernel for live leaf cohorts.
- Added provisional saturating irradiance response with bounded temperature, water, and nutrient factors.
- Added atmospheric carbon uptake reporting and reserve-carbon additions to plant root pools.
- Added tests for assimilation amount, stress-factor scaling, dead/no-leaf behavior, noncarbon material preservation, and invalid inputs.
- Updated roadmap, biology docs, and evidence documentation.

### Evidence and verification

- `python -m pytest tests/unit/biology` passed with 17 tests.
- `ruff check src/arboria/biology tests/unit/biology` passed.
- `mypy src tests/unit` passed.

### Limitations

- Carbon-assimilation baseline only: no canopy shading, root/substrate uptake, nutrient chemistry, respiration, stress, damage, death, species calibration, persistence integration, commands, or UI exists yet.
