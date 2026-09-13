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

## M-004 — Parenthesized `nonlocal` tuple in server state (2026-09-14)

- **Observed:** `src/arboria/app/server.py` used `nonlocal (a, b, ...)` when threading nursery zone/reservoir state through lifespan/tick/restore closures, producing `SyntaxError: invalid syntax` at test collection.
- **Cause:** The agent assumed `nonlocal` accepts a parenthesized target list like a tuple.
- **Impact:** Unit collection failed for server/nursery API suites; no commit, data loss, or repository modification occurred.
- **Correction:** Replaced parenthesized lists with comma-separated `nonlocal` statements before rerunning gates.
- **Prevention:** Use one `nonlocal name1, name2, ...` statement per scope; run targeted imports/tests immediately after editing closure state.

## M-005 — Full-target soak exceeded execution budget (2026-09-14)

- **Observed:** The requested 500-plant, ten-sim-year headless soak built in
  0.71 seconds but exceeded its 900-second execution budget during the
  1,051,200-tick run.
- **Cause:** The current pure-Python nursery still performs repeated
  full-organ-list work in growth and per-plant assimilation.
- **Impact:** At that point the target-scale decade-stability gate remained open;
  no final checkpoint or stability claim was recorded from the timed-out run.
- **Correction:** Profiled and reduced the remaining full-list work, then reran
  the same target-scale command successfully in 853.22 seconds. The earlier
  timeout remains historical evidence; it is not treated as the final result.
- **Prevention:** Profile before extending soak budgets, and keep timeout
  outcomes distinct from passes in the evidence record.

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
