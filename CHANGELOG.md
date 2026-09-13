# Changelog

Records delivered work and actual evidence. Planned features belong in [ROADMAP.md](ROADMAP.md), not in claims of implemented behavior.

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
