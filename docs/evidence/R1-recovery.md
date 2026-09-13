# R1 crash recovery, migration, and atomic-save evidence

## Scope

- Startup no longer fails when the recorded active checkpoint is corrupt or
  missing. `CheckpointWriter.fallback_checkpoint_id` walks the manifest
  parent chain for the first fully loadable generation; the server repoints
  the active checkpoint at the fallback (or clears it and boots starter
  state when nothing loads) with warning logs. Corrupt generations are
  skipped, never repaired or trusted.
- `load_nursery_state` in `src/arboria/sim/nursery.py` is the single
  versioned migration entry used by startup and restore: schema versions
  1–4 load with starter fallbacks for keys their era lacked, and versions
  outside that range are rejected instead of guessed at.
- Checkpoint creation stays atomic: state and manifest are written into a
  hidden `.tmp` generation and published with one `os.replace`. A mid-write
  crash leaves only the `.tmp` directory, which startup cleanup removes;
  the active checkpoint and metadata never point at partial state.

## Verification

- `python -m pytest tests/unit` passed with 138 tests, including injected
  mid-write `OSError` (no final dir, active unchanged, cleanup removes the
  `.tmp`, next save succeeds), parent-chain fallback past corrupt
  generations, `None` when everything is corrupt, malformed-ID rejection,
  synthetic v1/v2/v4 migration loads, newer/invalid version rejection,
  corrupt-active startup recovery to parent or starter state, and a
  read-only checkpoints directory producing HTTP 500 with the server alive,
  no residue, and saves working after permissions return.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- `npm --prefix web run check/test/build` passed (16 frontend tests; no
  frontend changes in this slice).
