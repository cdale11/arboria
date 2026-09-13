# Arboria

A persistent, biologically grounded nursery and plant-shop simulation with procedural visuals, evolving plants, and a companion that learns to manage the shop.

## Project status

**Authenticated living-nursery baseline with two ticking starter plants, inspection projections, clock/save controls, and metadata-plus-biology checkpoints. No water/nutrient uptake, species catalog, shop economy, companion, procedural 2.5D rendering, or touch controls have been implemented yet.** The documents in this repository define intended behavior and delivery gates; they are not evidence that the described features work. See [ROADMAP.md](ROADMAP.md) for implementation status.

## The game

- Organ-level plants: roots, branches, buds, leaves, flowers, fruit, and seeds interact through water, carbon, nutrients, development, and environmental conditions.
- A temperate outdoor nursery and controlled greenhouse support trees, bonsai, herbs, vegetables, succulents, and houseplants.
- Sell plants, propagated stock, and products; manage substrates, fertilizers, compost, inventory, demand, and production.
- A full-authority shop companion starts with competent care and learns from outcomes and player actions. Explicit protections constrain sales, pruning, spending, and other actions.
- Procedural 2.5D graphics and mouse, keyboard, and touch controls. No external art is required by the design.
- Strict biological consequences, including death. Relaxation comes from understandable controls and useful automation, not hidden immunity.
- Open-ended combinations of inherited traits, environmental interactions, recipes, and learned strategies. Experimental AI-proposed mechanics are a later, separately validated research release.

## Agreed operating model

| Setting | Contract |
| --- | --- |
| World | One persistent shop, shared by the owner's devices |
| Listen address | `0.0.0.0` |
| Default port | `8765`, configurable |
| Authentication | Shared password with server-side sessions |
| Default time | 1 simulated day per 30 real minutes; configurable |
| Client disconnected | Simulation, care, training, and commerce continue |
| Server stopped | No simulated time passes; resume saved time |
| Initial target scale | 500–1,000 living plants; performance must be measured |
| Primary language | Python; TypeScript for the browser |
| Environment | Conda environment `arboria`; npm permitted inside it |

The default calendar advances 48 simulated days per real day, or approximately one 365-day year per 7.6 real days. A plant's developmental requirements still determine its growth; trees do not become mature merely because the player opens a screen. Starter saplings and established stock make tree care immediately playable.

## Installation and launch

The current baseline provides one command from the repository root:

```bash
./run.sh
```

It locates Conda, activates `arboria`, ensures npm uses Conda's Node, installs locked browser packages if `web/node_modules` is absent, rebuilds browser assets when source/config fingerprints change, configures the local shared password on first run, acquires the data-directory process lock, and starts the FastAPI server. It currently serves only the honest dependency/auth baseline page and health/auth endpoints.

Python dependencies and Node must be installed through Conda. Browser packages use pinned npm dependencies and `npm ci` within activated `arboria`. No pip fallback is authorized. Runtime operation after initial installation/build must not require internet access. The current direct dependency policy is recorded in [dependency policy](docs/dependencies.md).

Authentication uses one shared local password, HttpOnly SameSite session cookies, a readable session-bound CSRF cookie for authenticated mutations, same-origin checks for unsafe requests, and a baseline failed-login throttle. First interactive run prompts for the password; unattended setup may use `ARBORIA_SETUP_PASSWORD` exactly once in a controlled local environment. On the host, open `http://localhost:8765`; on a trusted LAN, use the host's LAN address and port. `0.0.0.0` is a bind address, not the browser destination. Direct public-internet deployment is outside the first release's deployment contract.

The current server exposes authenticated world metadata at `/api/v1/world` and a simulation clock at `/api/v1/clock`, with CSRF-protected pause, resume, and speed controls. It also exposes the baseline command endpoint at `/api/v1/commands` for bounded, deduplicated, receipt-backed clock commands, `/api/v1/stream` for authenticated bounded WebSocket snapshot/ping messages, `/api/v1/saves/checkpoint` for manual checkpoint creation, `/api/v1/saves` plus `/api/v1/saves/named` for named save listing/creation, `/api/v1/saves/restore` for restore, and `/api/v1/plants` plus `/api/v1/plants/{id}` for living-nursery inspection. Checkpoints now include starter-plant biology in addition to metadata. World identity, request epoch, command receipts, clock state, tick count, world revision, active checkpoint ID, autosave timestamp, and named snapshots are stored in `world.sqlite3`; process restart keeps the world UUID, records a new timeline UUID/request epoch, recovers nursery biology from the active checkpoint when present, and resumes from the last saved clock/tick state without wall-clock catch-up. Full export/import, water/nutrient uptake, species catalog, economy, companion behavior, procedural nursery rendering, and horticultural command execution are not implemented yet.

## Saves and learning

The planned default data directory is `./var/`, relative to the repository root, overridable with `ARBORIA_DATA_DIR`. Autosaves, named snapshots, restore, and export/import will include biology, shop state, RNG state, training data, model weights, optimizer state, companion preferences, and rule versions. Live database copying is not a supported backup procedure; export will create a consistent archive. See [persistence](docs/persistence.md).

## Development

Read [AGENTS.md](AGENTS.md) before doing any work. Every development shell must activate the existing environment:

```bash
source /home/umang/miniconda3/etc/profile.d/conda.sh
conda activate arboria
```

This path is specific to the inspected development machine. The launcher must discover Conda rather than hard-code that path.

Current verification commands:

```bash
python -m pytest tests/unit
ruff check .
mypy src tests/unit
PATH="$CONDA_PREFIX/bin:$PATH" npm --prefix web run check
PATH="$CONDA_PREFIX/bin:$PATH" npm --prefix web run test
PATH="$CONDA_PREFIX/bin:$PATH" npm --prefix web run build
```

These are baseline smoke checks only. The first playable release must supply the broader verification commands and suites described in [testing](docs/testing.md). Dependency and launcher smoke checks are recorded in `CHANGELOG.md`.

## Specification index

- [Decision register](docs/decisions.md): confirmed choices, engineering defaults, unresolved release gates.
- [Game design](docs/game-design.md): interaction, calendar, shop, autonomy, and release coverage.
- [Architecture](docs/architecture.md): module ownership, data structures, tick order, API, concurrency, launch.
- [Dependency policy](docs/dependencies.md): selected Conda/npm direct dependencies and lock regeneration.
- [Biology](docs/biology.md): units, numerical contracts, functional–structural modeling, evidence.
- [Learning](docs/learning.md): online models, training, authority, emergence, rule invention.
- [Persistence](docs/persistence.md): transactions, complete checkpoints, recovery, migrations.
- [Testing](docs/testing.md): invariants, scenarios, operational and performance gates.
- [ROADMAP.md](ROADMAP.md): dependency-ordered, complete deliverables.
- [CHANGELOG.md](CHANGELOG.md): actual changes and verification.
- [MISTAKES.md](MISTAKES.md): observed mistakes and prevention.

Specifications are normative unless explicitly labeled a hypothesis, provisional target, or unresolved gate. Scientific fidelity and performance require evidence; neither unlimited emergence nor absence of all bugs is promised.
