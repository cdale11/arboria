# R1 Stream Baseline Evidence

## Scope

- Added authenticated `/api/v1/stream` WebSocket endpoint.
- Rejected unauthenticated or cross-origin WebSocket upgrades.
- Sent initial bounded world/clock snapshot messages with schema version, world UUID, timeline UUID, revision fields, request epoch, and clock status.
- Added a minimal ping/pong control message and rejected oversized inbound messages.

## Evidence

- `python -m pytest tests/unit/app/test_server.py` passed with 19 tests and the documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check src/arboria/app/server.py tests/unit/app/test_server.py` passed.
- `mypy src tests/unit` passed.

## Limitations

- This was the initial stream protocol baseline.
- Biological projections, revisioned deltas, and resync recovery were added later in `docs/evidence/R1-stream-resync.md`.
- Persistent reconnect replay, outbound subscriber queue limits, detailed inspection subscriptions, and frontend stream consumption remain unimplemented.
