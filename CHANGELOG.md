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
