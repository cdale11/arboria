# Persistence, restore, and recovery

## 1. Required guarantees

- A checkpoint represents one committed simulation boundary across biology, economy, pending actions, and learning.
- A crash may lose work since the last durable checkpoint; it cannot expose a mixture of different checkpoint generations as a valid world.
- Default autosave interval is 60 real seconds while running, plus graceful shutdown and explicit named snapshots. Display the last successful durable save time and any error.
- Client absence does not affect saves. Server downtime does not advance simulation time.
- Restoring includes the learning history that belonged to that snapshot, not the newest model from another timeline.
- Export is a verified portable archive; it excludes passwords and sessions by default.

## 2. Data directory

Current partial layout:

```text
var/
  world.sqlite3          # Implemented R1 metadata: world identity, timeline identity, clock state
  checkpoints/<id>/      # Implemented R1 metadata-only checkpoint generations
  auth/                  # Password hash and session storage, private permissions
  server.lock            # OS-backed lock target
```

Planned additions:

```text
var/
  world.sqlite3          # Later also stores committed checkpoint references and receipts
  exports/               # User-requested backup archives
  logs/                  # Bounded operational logs; no secrets
```

`ARBORIA_DATA_DIR` overrides the root. Test fixtures use isolated temporary directories. Never load executable pickle/joblib content from a save. Numerical arrays use a non-executable format with explicit shapes/dtypes and `allow_pickle=False` where applicable.

## 3. Versioned metadata

Implemented R1 metadata currently records one `worlds` row with world UUID, process-start timeline UUID, schema version, request epoch, optional active checkpoint ID, creation/update timestamps, clock `sim_time_seconds`, `speed`, `paused` fields, `sim_tick`, `world_revision`, and consumed simulation time. Startup keeps the world UUID, rotates the timeline UUID/request epoch, and loads the saved clock/tick state without adding elapsed wall time while the server was stopped.

Implemented R1 checkpoints are immutable metadata-only generations under `checkpoints/<checkpoint_id>/` with `manifest.json` and `state.json`. They record the current world/timeline/request epoch, clock, tick/revision state, receipt count, and purpose (`manual` or `autosave`), then register a complete checkpoint row and active checkpoint ID in SQLite. Metadata-only named snapshots can point to these checkpoints through the `snapshot_names` table. Metadata-only autosave writes checkpoints after the configured interval when authenticated world status is observed and stores the last autosave timestamp. Metadata-only restore validates the manifest ID, `state.json` size, and SHA-256 before restoring clock/tick state with a fresh timeline and request epoch. Startup removes hidden `*.tmp` checkpoint directories left by interrupted generation writes before opening mutable metadata, then validates the active checkpoint if one is recorded. Checkpoints do not yet contain biology, economy, learner arrays, RNG streams, pending queues, export/import, or retention behavior.

Minimum full SQLite entities:

| Entity | Required fields |
| --- | --- |
| `worlds` | world UUID, active timeline UUID, schema version, active checkpoint ID |
| `checkpoints` | ID, parent ID, sim tick, world revision, real creation timestamp, manifest hash, status |
| `snapshot_names` | name, checkpoint ID, creation timestamp, protected flag |
| `command_receipts` | timeline, request epoch, command ID, actor, sequence, status, result, expiry policy |
| `migration_history` | from/to schema, tool version, timestamp, backup reference |

The immutable checkpoint contains authoritative serialized domain state, including the command receipt/deduplication state required at that boundary. SQLite receipt tables may index current results, but after recovery they must reconcile to the selected checkpoint. Do not leave an "applied" receipt pointing to an action absent from recovered state.

Manifest fields:

```text
format_version, world_id, timeline_id, checkpoint_id, parent_checkpoint_id
sim_tick, sim_time_seconds, speed, paused, world_revision
engine_version, dependency_lock_hash, platform_numerical_metadata
catalog_versions, rule_set_hash, active_model_ids
files[{relative_path, size_bytes, sha256, dtype?, shape?, domain_schema_version}]
random_stream_metadata, pending_event_count, command_sequence_counter, request_epoch
```

Validate paths remain beneath the checkpoint root. Validate sizes, hashes, shapes, finite numerical arrays where required, ID references, topology, and version compatibility before loading. Hashes detect corruption, not malicious authenticity; imported data still requires validation and resource limits.

## 4. Atomic checkpoint protocol

1. At a tick boundary, capture an immutable, mutually consistent state view. Freeze learner state at an acknowledged boundary or include its last complete checkpoint plus explicit pending scheduling state; never read tensors while an optimizer updates them.
2. Write a new temporary generation directory. Serialize domain arrays, RNG states, pending commands/events, model/optimizer/replay state, policies, and manifests. Bound memory; do not duplicate a multi-gigabyte world without accounting.
3. Flush/fsync files and manifest, then atomically rename the generation on the same filesystem and fsync the parent directory.
4. In one SQLite transaction, register the complete generation and advance the active checkpoint reference and matching receipt indexes. Use appropriate durable SQLite settings; document WAL/synchronous choices and test them.
5. Acknowledge durable save only after commit. Old generations remain until retention permits deletion.

Crash before step 4 leaves an unreferenced generation, not an active partial save. Crash after step 4 must leave all referenced files durable under the supported local-filesystem contract. Do not claim these guarantees for arbitrary network filesystems without tests.

Garbage collection deletes only unreferenced, non-named generations after a verified successful save, retaining at least the latest five autosaves and one pre-migration/pre-restore snapshot. Named snapshots are never silently evicted. Surface disk usage and explicit deletion controls.

## 5. Restore

1. Authenticate the request and show target date, world, and progress-loss summary.
2. Stop command admission and pause at a safe boundary; cancel/join or invalidate background training.
3. Validate the target in isolation. An invalid import cannot change the live world.
4. Create a durable pre-restore snapshot of the current world. If disk failure prevents it, fail restore clearly rather than erase the current state.
5. Load all domains together; assign a new timeline UUID and persist a restored-generation checkpoint. Preserve historical provenance of the source timeline.
6. Clear pending client sessions' projection state and reject commands/training results from the old timeline. Existing login may remain, but each device must resync the world.
7. Resume with the saved pause/speed policy, displaying restore completion.

Saved pending biological and manager events remain valid under the restored state. Old in-flight HTTP commands from the abandoned timeline cannot be replayed into it. A new world also receives a new world UUID; importing a copy must avoid cross-world command identity collisions.

Process restart also creates and durably records a fresh timeline before admitting clients, because a crash may have abandoned acknowledged but not yet autosaved progress. Retain loaded pending commands/events with their provenance and explicitly rebind internally accepted work to the recovered timeline; do not accept external retries from the old timeline. The restart timeline change does not advance simulation time or reset learned biological state. Deterministic continuation tests compare scientific/learner state while allowing this intentional identity change.

## 6. Complete learner state

Store weights, optimizer moments, step counters, architecture/feature schema, normalization statistics, replay ordering/cursor, training and holdout partitions, delayed outcome labels, preference model, RNG streams, active/candidate metadata, evaluation anchors, budget counters, and accepted activation history. A candidate mid-gradient computation need not be saved; its scheduling/retry semantics must be explicit and testable.

Ordinary asynchronous scheduling is reproducible through recorded activation history only within the declared limits. Deterministic test mode uses synchronous training barriers for save/resume equivalence. Do not promise cross-backend bitwise identity.

## 7. Failure handling and migration

- Disk full: keep the last valid checkpoint; notify UI/logs and pause state progression after a failed mandatory checkpoint to avoid unbounded unsaved work. Read-only inspection remains available.
- Corrupt active generation: do not silently discard progress. Offer validated older generations with their dates and require owner selection, or follow an explicitly configured recovery policy.
- Unsupported newer schema: refuse load with version information, without rewriting files.
- Migration: back up, migrate into a new generation, validate, then atomically switch; never modify the only valid save in place.
- Missing model/rule version: refuse incompatible load; no fresh random model or replacement rule masquerading as continuation.
- Import: enforce archive entry/path/count/expanded-size limits and reject links/path traversal. Validate before activation.
- Shutdown interruption: recover the latest durable committed checkpoint. Pending effects and commerce cannot be applied twice within the recovered timeline.

Backups should be restorable on another supported Linux x86-64 installation with matching locks, independently of the original absolute data path. Host credentials are created separately after import.
