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
- Current-domain export/import wraps validated checkpoint manifest/state JSON
  in a bounded base64 zip archive. Import rejects malformed archives, extra
  entries, oversize entries, unsupported export metadata, and invalid
  checkpoint hashes before registration or restore.

## Verification

- `python -m pytest tests/unit/app/test_checkpoints.py tests/unit/app/test_shop_api.py`
  passed with 21 tests, including export/import archive round trip, import
  entry validation, endpoint invalid-base64 rejection, and restoring protected
  plant state from an imported current-domain archive.
- Prior full evidence: `python -m pytest tests/unit` passed with 138 tests, including injected
  mid-write `OSError` (no final dir, active unchanged, cleanup removes the
  `.tmp`, next save succeeds), parent-chain fallback past corrupt
  generations, `None` when everything is corrupt, malformed-ID rejection,
  synthetic v1/v2/v4 migration loads, newer/invalid version rejection,
  corrupt-active startup recovery to parent or starter state, and a
  read-only checkpoints directory producing HTTP 500 with the server alive,
  no residue, and saves working after permissions return.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- Current-domain export/import does not include learner arrays, optimizer,
  replay, RNG streams, or companion policy state because those systems do not
  exist yet.
