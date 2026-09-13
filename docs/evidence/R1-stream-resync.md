# R1 stream resync and revisioned deltas — evidence

## Scope

- `/api/v1/stream` now sends an authenticated initial `snapshot` containing
  world/timeline identity, request epoch, clock, loop, and nursery biological
  projections.
- Inbound messages are parsed as JSON and remain bounded to 4096 bytes.
- `ping` still returns `pong`; when the ping causes the server-owned clock to
  advance one or more world revisions, the server first emits a revisioned
  `delta` frame with `base_revision` equal to the previous revision and a full
  nursery projection payload.
- `sync {base_revision}` supports reconnect/resync. A current or future base
  returns `synced`; a stale base returns an authoritative replacement
  `snapshot` with `base_revision: 0`. R1 does not retain a persistent delta
  log, so stale clients get a full projection instead of replay.

## Verification

- `python -m pytest tests/unit/app/test_server.py` passed with 38 tests,
  including authenticated initial snapshots, current-revision `sync`, stale
  `sync` replacement snapshots with biological projections, real tick-driven
  `delta` emission at 144x speed, oversized-message close, unauthenticated
  close, and cross-origin close.
- Full gate evidence is recorded in the changelog entry for this slice.

## Limitations

- Deltas are ephemeral full-projection deltas, not retained patch logs.
- There is no persistent replay, outbound subscriber queue implementation,
  detailed inspection subscription, or frontend WebSocket consumer yet.
