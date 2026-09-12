# Mistakes and prevention

This is an incident log, not a list of imagined failures. Add entries when an actual agent error is observed. Record the date, cause, impact, correction, and prevention. Correct old entries openly rather than erasing history.

## M-001 — Environment discovery outside `arboria` (2026-09-12)

- **Observed:** The initial environment-discovery shell ran before `arboria` was activated; the inherited active environment was `eidolon`.
- **Cause:** The agent treated environment discovery as an exception to the user's all-shells requirement.
- **Impact:** Read-only environment inspection; no dependencies or project files were changed by that command.
- **Correction:** Subsequent shell commands explicitly source Conda and activate `arboria` first.
- **Prevention:** Every shell command, including Git and hardware inspection, must use the activation prefix. Dedicated filesystem tools need no shell activation.

## M-002 — Unborn Git history stopped an inspection chain (2026-09-12)

- **Observed:** `git log --oneline -10` failed because the empty repository had no commits. Commands chained after it did not run.
- **Cause:** The inspection assumed a populated Git history.
- **Impact:** Hardware inspection had to be rerun; no data loss or repository modification.
- **Correction:** Hardware inspection was rerun separately; the repository's unborn state was recognized.
- **Prevention:** Check for a valid `HEAD` before history-dependent operations in an empty repository. Do not interpret an expected absence of history as failure of unrelated checks.

## M-003 — Conda npm invoked NVM node through `PATH` (2026-09-12)

- **Observed:** `$CONDA_PREFIX/bin/npm --prefix web install --package-lock-only` emitted an engine warning showing Node `v24.19.0`, even though `$CONDA_PREFIX/bin/node` was `v26.5.1`.
- **Cause:** The inherited shell `PATH` put an NVM Node directory before the Conda environment. The Conda npm executable used `/usr/bin/env node`, so it found the wrong Node binary.
- **Impact:** A package-lock generation command ran with the wrong Node binary. No runtime code or application state was changed.
- **Correction:** Regenerate npm locks and run npm checks with `PATH="$CONDA_PREFIX/bin:$PATH"` after activating `arboria`.
- **Prevention:** For any Node/npm command, use activated `arboria` plus a `PATH` prefix that makes `$CONDA_PREFIX/bin/node` the first `node`. Verify `node -v`, `npm -v`, and `command -v node` before dependency or frontend checks.

## Anticipated risks — not observed incidents

These are design-review reminders, not claims that errors have happened:

- Using client connectivity or rendering level of detail to decide whether plants live or grow.
- Saving model weights without optimizer, normalization, random-stream, or replay state.
- Training on outcomes from before a save restore and leaking the abandoned future into a restored world.
- Treating a predictive network as an authority that can create water, nutrients, or money.
- Assuming GPU acceleration is beneficial without measuring memory and transfer costs.
- Replacing meaningful learned behavior with scripted claims of "AI".
- Adding npm/pip/system tools outside the agreed environment policy.
- Describing planned controls, tests, or launcher behavior as already working.
- Calling model-mediated gameplay parameters scientifically validated without sources and calibration.
- Hiding unsupported species behind plausible-looking generic parameters.
