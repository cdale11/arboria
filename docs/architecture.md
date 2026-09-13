# Architecture and implementation contracts

This specifies intended code, not existing modules. Public interfaces below establish ownership and semantics; implementation may refine names without changing contracts. Changing contracts requires a decision record.

## 1. Target and dependency policy

Inspected target: Linux x86-64, AMD Ryzen 3 8300GE, 4 cores / 8 threads, Radeon 740M-class integrated graphics, approximately 6.9 GiB usable system RAM. At inspection approximately 3.7 GiB was available; that is not a permanent allocation. CPU flags include AVX2 and AVX-512, but compiled artifacts must declare their portability and never assume flags on a different host.

Baseline stack: Python 3.13, NumPy, optional Numba, FastAPI, Uvicorn, SQLite; TypeScript, Three.js, Vite. Conda supplies Python, Node, native libraries, Python tools, and test tools. npm supplies browser dependencies locally within activated `arboria`. Exact installed versions are locked in `conda-linux-64.lock` and `web/package-lock.json`; direct dependency rationale is in `docs/dependencies.md`.

Check in a human-readable environment specification and a machine-resolved Linux x86-64 Conda lock covering transitive packages, channels, and builds. Check in `package-lock.json`; use `npm ci`. Document tools used to regenerate locks. A candidate library unavailable through the allowed managers triggers clarification, not a pip fallback.

Do not add Redis, a message broker, microservices, distributed training, Kubernetes, or a vector database without evidence of a concrete requirement. SQLite is sufficient for one local authoritative world.

## 2. Planned source ownership

```text
src/arboria/
  app/           # Composition, lifecycle, configuration, process lock
  sim/           # Tick scheduler, world ownership, command ordering, events
  biology/       # Pure numerical kernels, organ development, resource budgets
  environment/   # Climate, zones, light, substrate and later compost ecology
  catalog/       # Versioned species, items, parameter validation and provenance
  economy/       # Inventory, quotes, demand, transaction rules
  companion/     # Planning, protections, learned preferences, explanations
  learning/      # Numerical models, optimizer, datasets, evaluation, activation
  persistence/   # SQLite, checkpoint manifests, migrations, backup/restore
  api/           # Authentication, HTTP/WebSocket schemas, client projections
web/src/
  api/           # Typed protocol client, reconnect, command receipts
  render/        # Procedural meshes, instancing, camera, visual LOD
  ui/            # Panels, controls, accessibility, input adapters
  state/         # Client projection only, no authoritative simulation
tests/
  unit/ integration/ scenarios/ persistence/ performance/
web/tests/
docs/
```

Do not create empty modules to imitate this tree. Add each module with implemented behavior and tests. Shared types belong to their owning domain; avoid a growing catch-all utilities module. `biology/` may import numerical and domain types, never HTTP, SQL, wall clocks, or renderer code.

## 3. World state and identity

Stable IDs are unsigned 64-bit counters, never reused within a timeline. Persist allocation counters. API encodes IDs as decimal strings to avoid JavaScript integer precision loss. Each world has a UUID; each restore or process restart creates a fresh timeline UUID, invalidating pre-recovery commands and training results. An ID's external identity is qualified by world and timeline, so restoring an older allocation counter cannot alias an abandoned future object.

Use structure-of-arrays storage for hot numeric data. Organ rows refer to stable IDs; an ID-to-row map handles compaction. Deletion uses tombstones until a safe boundary; never expose row indexes externally. Start with float64 for resource accounting, float32 for visual projection, explicit integer ticks and currency. Use narrower scientific arrays only after error-budget evidence.

Suggested organ columns:

```text
organ_id:u64  plant_id:u64  parent_id:u64?  kind:u8  alive:bool
created_tick:u64  developmental_stage:u16
length_m:f64  radius_m:f64  surface_area_m2:f64
structural_carbon_kg:f64  reserve_carbon_kg:f64
water_kg:f64  nitrogen_kg:f64  phosphorus_kg:f64  potassium_kg:f64
damage_fraction:f64  local_orientation:quaternion
```

Additional tissue-specific tables avoid allocating every possible trait for every organ. Species parameters are immutable shared catalog records, with individual genotype/phenotype modifiers stored separately. Leaf/root cohorts carry counts and aggregate area; buds and prunable structural branches remain individually identifiable. Cohort subdivision must conserve all extensive quantities.

Structural parentage is acyclic. R3 grafts add a separate typed vascular-connection table rather than corrupt parentage to represent transport links. Resource transfer across grafts must use a bounded network solve with explicit accounting; a graft does not merge plant identities or ownership implicitly.

World owns clock, catalog versions, plants, zones, inventory, economy, manager policy, random streams, learner activation IDs, pending events, and an ordered command queue. Clients receive bounded projections, not arbitrary internal object graphs.

### Domain interfaces

```python
def validate_command(world: WorldView, command: Command) -> ValidatedCommand | Rejection: ...
def apply_command(world: MutableWorld, command: ValidatedCommand) -> CommandResult: ...
def advance_biology(state: BiologyState, forcing: Forcing,
                    dt_seconds: float, params: ParameterView) -> BiologyDelta: ...
def plan_actions(observation: ManagerObservation, policy: ManagerPolicy,
                 predictor: PredictorView) -> tuple[ProposedAction, ...]: ...
def train_batch(checkpoint: LearnerState, batch: TransitionBatch,
                budget: TrainingBudget) -> TrainingResult: ...
```

Numerical kernels receive explicit arrays and elapsed simulation seconds. Their outputs include flux accounting and diagnostic flags. They neither mutate unrelated domains nor draw hidden global random numbers. Random inputs or domain-owned explicit streams must be passed where needed.

## 4. Tick ordering

One writer executes this versioned order per 300-second simulated tick:

1. Drain a bounded command batch; check world/timeline/revisions and revalidate protections, quotes, resources, and targets. Apply accepted actions in persisted enqueue order.
2. Advance prescribed forcing for the interval: sun/weather/zone settings; use interval means or bounded substeps where needed.
3. Compute root-zone and canopy exchanges with coupled plant water/carbon/nutrient fluxes. Debit shared zone supplies jointly, not once per plant.
4. Apply respiration, maintenance, stress, allocation, development, damage, and mortality. Generate topology changes at defined growth cadence.
5. Process due reproduction, decomposition, demand, and commerce events supported by this release. Event ties use stable sequence IDs.
6. Record outcomes and training transitions with pre-action observations, time, version, and masks. No future labels enter observations.
7. Run emergency manager checks; every sixth tick run broader planning. Enqueue actions for the next tick through the ordinary command path.
8. Validate and activate eligible background training results; build immutable next training inputs within memory budget.
9. Increment tick/revision and publish projections; prepare a checkpoint when due.

Cadences are simulation-time based. Numerical substeps may subdivide a tick for stability; changing the speed factor cannot alter the scientific timestep. Cohort growth allocation initially runs every 12 ticks (one simulated hour); conservation pools still update each tick. Markets initially clear hourly; exact demand preset is versioned.

The first tick performs emergency planning before normal unattended progression starts if no pending caretaker actions exist. No client request can reenter a numerical kernel. Long operations must not hold the simulation owner waiting for network/disk clients.

Current R1 implementation has a single in-process `WorldLoop` accumulator that consumes persisted clock state into 300-sim-second `sim_tick` and `world_revision` boundaries, with a bounded maximum of 100 ticks per drain. It does not run biological kernels, event processing, manager planning, or checkpoint scheduling yet.

The writer services lifecycle controls (pause/resume, speed, save, restore, shutdown) between ticks even when biological progression is paused. These controls cannot depend on the next biological tick to execute: otherwise a paused world could never resume. Current R1 implementation applies horticultural commands immediately against the frozen tick while paused rather than queueing them; a paused command queue with explicit limits and reserved lifecycle admission remains future work.

## 5. Commands and protocol

All messages have `schema_version: 1`. HTTP base: `/api/v1`. WebSocket: `/api/v1/stream`.

Command envelope:

```json
{
  "schema_version": 1,
  "command_id": "client-generated UUID",
  "world_id": "UUID",
  "timeline_id": "UUID",
  "request_epoch": 7,
  "kind": "water",
  "expected_target_revision": 42,
  "payload": {"plant_id": "123", "water_kg": 0.2}
}
```

The server derives actor identity/authority; clients cannot claim to be a privileged companion. Reject unknown fields where ambiguity is unsafe, nonfinite numbers, invalid units, negative amounts, unknown kinds, oversized batches, unauthorized targets, and stale relevant revisions. Global world revision changes alone should not invalidate unrelated plant actions.

`POST /commands` returns an acceptance receipt with status `queued`, `rejected`, or a previous result for a duplicate ID. Execution later produces `applied` or `rejected` with reason and resulting target revision. HTTP receipt is not proof of execution. Store deduplication/results with checkpoint state; bound retention with documented expiry and reject expired replay envelopes rather than execute them again.

Current R1 implementation uses `/api/v1/commands` for bounded, receipt-backed clock commands (`clock.pause`, `clock.resume`, `clock.set_speed`), nursery watering (`nursery.water` with `plant_id` and bounded `water_kg`), and shop commands (`shop.buy_water` with bounded `water_kg`, `shop.buy_plant` with `species_id`, `shop.sell_plant` with `plant_id`). It rejects unknown envelope fields, invalid UUIDs, unsupported schema versions, nonfinite payload numbers, oversized/nested payloads, stale world/timeline/request-epoch values, unknown command kinds, invalid clock payloads, insufficient cash, exhausted buyer demand, dead/unknown plant sales, and reservoir overflow. Receipts are persisted in SQLite and duplicate command IDs within the active timeline/epoch return the original receipt. Queued tick execution, receipt expiry/rotation policy, and checkpoint reconciliation are not implemented yet.

Use a server-issued request epoch obtained from the current snapshot. Only the current epoch accepts new commands. Rotate at most daily in real time or when a documented receipt-count cap is reached; persist the epoch and use a new timeline on restart. A rotation rejects old-epoch new submissions, while already accepted pending commands retain their receipts through execution. Never evict a receipt while its epoch still admits retries. A client encountering expiry must resync and obtain user intent again rather than silently resubmit a mutation under a new ID. Deduplication keys include timeline, epoch, and command ID.

Read endpoints: `/world`, `/plants/{id}`, `/catalog`, `/shop`, `/companion`, `/saves`, `/health`. Mutating save/export/restore routes require authentication and the same owner orchestration rules. A minimal health response exposes process readiness/lag, no secrets or detailed plant data.

Stream messages carry `world_id`, `timeline_id`, `revision`, `base_revision`, `kind`, and payload. Deltas are applied only to matching base revisions; otherwise fetch a new snapshot. Bound each subscriber's outbound queue; drop stale deltas and request resync rather than accumulate memory. Detailed inspection subscriptions limit organ payloads.

Current R1 implementation provides `/api/v1/stream` with authenticated and same-origin WebSocket upgrade checks, a bounded 4096-byte inbound message limit, an initial `snapshot` message containing world identity, timeline, request epoch, and clock status, plus `ping`/`pong`. Biological projections, revisioned deltas, reconnect replay, subscriber queues, and resync recovery are not implemented yet.

## 6. Authentication and single-instance operation

Current baseline first-run password input uses hidden terminal input with confirmation through `run.sh`; noninteractive setup may use `ARBORIA_SETUP_PASSWORD`, and noninteractive startup without configured credentials fails clearly. The current implementation stores a salted PBKDF2-HMAC-SHA256 hash with 600,000 iterations under `var/auth/auth.json`, stores only session-token and CSRF-token SHA-256 digests in `var/auth/sessions.json`, expires sessions after seven days, and never puts tokens in URLs. Future hardening may replace PBKDF2 if a stronger vetted password-hashing package is selected under policy.

Cookies are SameSite. The session cookie is HttpOnly; the CSRF cookie is readable by client code and must be copied into the `X-Arboria-CSRF` header for authenticated unsafe requests. Unsafe requests with an `Origin` or `Referer` not matching the request host are rejected. Failed logins are throttled in memory by client address. Secure cookies are required for HTTPS deployments but are not active on the current LAN HTTP baseline. Add persistent/distributed rate limiting and WebSocket upgrade checks before exposing real state-changing game actions. Same-origin frontend/API is the default. Plain LAN HTTP does not encrypt traffic; document the deployment boundary and optional TLS reverse-proxy contract before supporting remote exposure.

The current server acquires an OS-backed advisory `flock` on `server.lock` in the data directory during FastAPI lifespan startup and holds it until shutdown. A second server using the same data directory fails instead of creating a second owner. The lock file records the owning PID for diagnostics, but ownership is the kernel lock, not a stale PID file. Future world startup must acquire this lock before opening mutable world/checkpoint state. Graceful shutdown stops admission, finishes the current safe boundary, checkpoints, releases the lock, and exits once those systems exist.

## 7. Learning concurrency and performance

Start with one bounded background training worker. Benchmark thread versus process overhead; do not copy the entire world into a worker. Training inputs are compact immutable batches; results include timeline, source checkpoint, feature schema, model architecture, and rule/catalog versions.

Cap numeric library thread counts initially to avoid eight-thread BLAS competing with ticks and rendering. Use at most two training CPU threads as a provisional default. Measure p50/p95/p99 tick latency, queue delay, process-tree RSS, training duty cycle, save time, and dropped client projections.

GPU training is optional and gated by actual end-to-end benefit, dependency availability, and peak shared memory. Never change biology depending on GPU availability. The remote phone renders on its own GPU; the host iGPU is not automatically used by remote browsers.

## 8. Launcher contract

`./run.sh` currently works as a baseline launcher for static assets and health endpoints. The complete R1 launcher must work from any caller working directory and paths containing spaces:

1. Resolve repository path; locate Conda via active installation or documented configuration.
2. Activate/create `arboria` under the explicit setup contract; never install system packages or alter global npm.
3. Check lock fingerprints. Synchronize the locked Conda environment when necessary, then use its Node/npm for `npm ci` when the frontend lock changes.
4. Build when source/lock/config fingerprints change; reuse verified assets otherwise. Interrupted builds must not replace a valid bundle.
5. Validate configuration, data-directory permissions, credentials, migrations, and port availability.
6. Start one server process with static assets and API; forward signals correctly and print usable local/LAN connection instructions without secrets.

Configuration: `ARBORIA_HOST`, `ARBORIA_PORT`, `ARBORIA_DATA_DIR`; persisted world settings own time scale/climate. Defaults are `0.0.0.0`, `8765`, repository `var/`. Invalid configuration fails before mutating data. Setup downloads are explicit and logged; ordinary starts with satisfied locks must work offline. Do not silently download models, artwork, or browser binaries while playing.
