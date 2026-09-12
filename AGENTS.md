# Mandatory agent operating procedure

Applies to the entire repository. These instructions govern implementation, documentation, verification, and delivery.

## 1. Read before acting

1. Read this file, `README.md`, `ROADMAP.md`, `MISTAKES.md`, and relevant specifications in `docs/`.
2. Inspect repository status and existing changes. Treat unfamiliar changes as user or concurrent-agent work until investigated.
3. Identify the exact deliverable and its dependencies in the roadmap. Do not silently change the agreed vision or acceptance criteria.
4. For nontrivial work, maintain a task list with one active step and evidence-based completion.
5. Clarify genuine ambiguity with the **ask-user question tool** before taking a consequential fork. If the harness lacks that tool, stop at the ambiguity and ask explicitly; do not invent an answer. Independent, nonblocked work may continue.

## 2. Environment and dependencies

- Run **every shell command** in an activated Conda `arboria` environment, including Git and checks. The environment already exists on the target machine.
- On this machine, use `source /home/umang/miniconda3/etc/profile.d/conda.sh && conda activate arboria && <command>`. Discover the installation on other machines.
- Dedicated read/edit tools do not need a shell. Use dedicated file tools; use the provided patch tool for edits when available.
- Install Python software, build tools, Node, and required native libraries using Conda. Browser dependencies may use npm inside activated `arboria`.
- No global npm installations, pip installs, system package installs, or unapproved package-manager fallbacks. If Conda cannot supply a necessary package, ask the user.
- Lock direct and transitive dependencies. Record supported versions and platform constraints. Never choose a library merely because it is fashionable.
- The current environment has Python 3.14. Compatibility with the selected numerical stack is **unverified**. R1 must resolve and lock a supported combination; never claim this was already tested.
- User permission to install useful tools does not remove environment restrictions. Ask if a tool cannot satisfy them.
- Never install or download model weights, assets, or software at runtime without a documented, explicit setup contract.

## 3. Engineering invariants

- Python owns the authoritative world. TypeScript renders projections and submits commands.
- One writer mutates the world; player and companion actions use the same validated command path.
- Use explicit units, bounded numerical operations, stable identifiers, schema versions, and resource accounting.
- Rendering detail cannot switch biological simulation on/off. No client-connected dependency in ticking, commerce, or training.
- Random streams, model state, learner progress, and pending events must be persistable and testable.
- Learning cannot bypass money, material conservation, compatibility rules, or user protections.
- No arbitrary runtime code generation/execution. Experimental mechanics must follow the restricted proposal/validation protocol.
- Keep modules small and domain-owned. No network, database, clock, or rendering imports inside pure biology kernels.
- Add types and public-contract documentation. Avoid unsupported abstraction layers, speculative services, and premature GPU dependencies.
- Never silently substitute fake learning, random price changes, or decorative branch generation for the specified systems.
- Feature claims must distinguish modeled, approximated, deferred, and unsupported behaviors.
- Do not introduce empty handlers, dummy data sold as simulation, disabled promised controls, TODO implementations, or placeholder releases.

## 4. Work and validation loop

1. State scope, relevant contracts, and intended evidence.
2. Make a coherent, maintainable change consistent with surrounding code.
3. Add meaningful tests for behavioral changes, invariants, regressions, persistence, and risky boundaries. Do not write tautological tests or tests for cosmetic edits alone.
4. Run targeted checks; then run the deliverable's mandatory gates. Repeat only when new changes or unresolved failures justify it.
5. Investigate failures. Never suppress a failing assertion, loosen a scientific tolerance, or update a golden result without a written cause and justification.
6. Update documentation and changelog in the same deliverable. Record actual mistakes in `MISTAKES.md`; keep hypothetical risks separately labeled.
7. Inspect the final diff for scope, secrets, generated artifacts, unsupported claims, and cross-document inconsistency.
8. Commit and push as described below. Report evidence and remaining blockers accurately.

A commit may be a complete internal improvement; a roadmap release is complete only when all its gates pass. Do not mark a partial release complete or expose unfinished features to players. If blocked, retain honest in-progress status and ask the user.

## 5. Git: user-requested commit and push

- The user explicitly requires **commit and push after every completed coherent change set**, including documentation-only work. Do not leave an intentionally delivered change uncommitted.
- Before each commit inspect `git status`, `git diff`, and `git log --oneline -10`. For an unborn branch, record that history does not exist and continue with the initial commit.
- Stage only intended files. Never stage passwords, session keys, saves, model checkpoints, local environment directories, or dependency caches.
- Use a concise descriptive message, following existing history when present; initial convention is `docs: ...`, `feat: ...`, `fix: ...`, or `test: ...`.
- Push to the configured remote/tracking branch. Initial branch is `main`, remote is `origin`.
- No force push, Git configuration changes, skipped hooks, destructive resets, empty commits, or amendments without explicit permission.
- If hooks reject a commit, fix the cause and create a normal commit. If push fails, report the failure and resolve it without overwriting remote work.
- After pushing verify clean intended status and that local HEAD equals the remote branch. Do not say "pushed" based only on local commit success.

## 6. Documentation requirements

- `README.md`: current runnable state, accurate setup/run/test/backup instructions, concise feature summary.
- `CHANGELOG.md`: every delivered change, rationale where useful, checks actually run, limitations.
- `ROADMAP.md`: ordered dependencies, scope, acceptance evidence, actual completion status.
- `MISTAKES.md`: actual error, impact, correction, prevention; never fabricate incidents.
- `docs/`: implementation contracts, schemas, units, equations, failure cases, evidence, and decisions.
- Keep confirmed user choices separate from engineering defaults and scientific hypotheses. Record deviations through a decision entry before implementation.
- Do not cite sources not inspected. Numerical biological parameters require provenance or an explicit provisional-calibration label.
- No tests or documentation can establish absolute bug-freedom. Use measurable guarantees and clearly scoped evidence.

## 7. Collaboration

- Design supports multiple agents through module boundaries, explicit contracts, and small coherent changes.
- Do not spawn subagents unless the user or applicable instructions explicitly request delegation. This document does not itself request delegation.
- If parallel work is authorized, assign nonoverlapping ownership, agree interfaces first, identify one integration owner, and run integration gates before delivery.
- Never overwrite another agent's changes or assume stale status is current.
- Use the question tool when requirements conflict, scientific assumptions are unresolved, or a deliverable cannot meet its gate.

## 8. Definition of done

A delivered change has implemented behavior (or complete documentation for a documentation deliverable), passing applicable checks, updated docs, no secret/generated-state leakage, a reviewed commit, a verified push, and a clear user-facing summary. A release additionally satisfies every listed acceptance criterion with recorded evidence.
