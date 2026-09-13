"""Bounded command envelope validation, deduplication, and receipts.

This module owns the wire contract for client mutations routed through
``POST /api/v1/commands``. Structural envelope failures fail the request;
identity/epoch mismatches, unknown kinds, and payload violations produce
persisted receipts so retries are idempotent within an epoch.
"""

from __future__ import annotations

import math
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from uuid import UUID

COMMAND_SCHEMA_VERSION = 1
MAX_DEPTH = 8
MAX_VALUES = 256
MAX_STRING = 1024
ENVELOPE_KEYS = frozenset(
    {
        "schema_version",
        "command_id",
        "world_id",
        "timeline_id",
        "request_epoch",
        "kind",
        "payload",
    }
)


class CommandValidationError(ValueError):
    """Raised when the envelope cannot be trusted enough to persist a receipt."""


@dataclass(frozen=True)
class CommandEnvelope:
    command_id: str
    world_id: str
    timeline_id: str
    request_epoch: int
    kind: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class Receipt:
    command_id: str
    actor: str
    kind: str
    status: str
    reason: str | None
    result: dict[str, Any] | None
    created_unix_s: int


SaveReceipt = Callable[[str, int, Receipt], None]
FindReceipt = Callable[[str, int, str], Receipt | None]
CommandHandler = Callable[[CommandEnvelope], dict[str, Any]]


def _validate_value(value: Any, depth: int, budget: list[int]) -> None:
    budget[0] += 1
    if budget[0] > MAX_VALUES or depth > MAX_DEPTH:
        raise CommandValidationError("payload is too large or nested")
    if isinstance(value, bool) or value is None or isinstance(value, int):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise CommandValidationError("nan or infinite numbers are rejected")
        return
    if isinstance(value, str):
        if len(value) > MAX_STRING:
            raise CommandValidationError("payload string exceeds the size limit")
        return
    if isinstance(value, list):
        for item in value:
            _validate_value(item, depth + 1, budget)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise CommandValidationError("payload object keys must be strings")
            _validate_value(item, depth + 1, budget)
        return
    raise CommandValidationError("payload contains an unsupported value type")


def parse_envelope(raw: Any) -> CommandEnvelope:
    if not isinstance(raw, dict):
        raise CommandValidationError("command envelope must be a JSON object")
    unknown = set(raw) - ENVELOPE_KEYS
    if unknown:
        raise CommandValidationError(f"unknown envelope fields: {sorted(unknown)}")
    missing = ENVELOPE_KEYS - set(raw)
    if missing:
        raise CommandValidationError(f"missing envelope fields: {sorted(missing)}")
    if raw["schema_version"] != COMMAND_SCHEMA_VERSION:
        raise CommandValidationError("unsupported command schema version")
    for key in ("command_id", "world_id", "timeline_id"):
        value = raw[key]
        if not isinstance(value, str):
            raise CommandValidationError(f"{key} must be a UUID string")
        try:
            UUID(value)
        except ValueError as exc:
            raise CommandValidationError(f"{key} must be a UUID string") from exc
    epoch = raw["request_epoch"]
    if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 1:
        raise CommandValidationError("request_epoch must be a positive integer")
    kind = raw["kind"]
    if not isinstance(kind, str) or not kind or len(kind) > 64:
        raise CommandValidationError("kind must be a short string")
    payload = raw["payload"]
    if not isinstance(payload, dict):
        raise CommandValidationError("payload must be an object")
    _validate_value(payload, 0, [0])
    return CommandEnvelope(
        command_id=raw["command_id"],
        world_id=raw["world_id"],
        timeline_id=raw["timeline_id"],
        request_epoch=epoch,
        kind=kind,
        payload=payload,
    )


class CommandService:
    """Persisted receipt and dispatch layer for R1-supported commands."""

    def __init__(
        self,
        *,
        world_id: str,
        timeline_id: str,
        request_epoch: int,
        save_receipt: SaveReceipt,
        find_receipt: FindReceipt,
    ) -> None:
        self._world_id = world_id
        self._timeline_id = timeline_id
        self._epoch = request_epoch
        self._save_receipt = save_receipt
        self._find_receipt = find_receipt

    def submit(
        self,
        envelope: CommandEnvelope,
        handler: CommandHandler,
        *,
        actor: str = "player",
    ) -> Receipt:
        existing = self._find_receipt(
            self._timeline_id,
            self._epoch,
            envelope.command_id,
        )
        if existing is not None:
            return existing
        if envelope.world_id != self._world_id or envelope.timeline_id != self._timeline_id:
            return self._record(envelope, "rejected", "world or timeline mismatch", None, actor)
        if envelope.request_epoch != self._epoch:
            return self._record(envelope, "rejected", "request epoch expired", None, actor)
        try:
            result = handler(envelope)
        except CommandValidationError as exc:
            return self._record(envelope, "rejected", str(exc), None, actor)
        return self._record(envelope, "applied", None, result, actor)

    def _record(
        self,
        envelope: CommandEnvelope,
        receipt_status: str,
        reason: str | None,
        result: dict[str, Any] | None,
        actor: str,
    ) -> Receipt:
        receipt = Receipt(
            command_id=envelope.command_id,
            actor=actor,
            kind=envelope.kind,
            status=receipt_status,
            reason=reason,
            result=result,
            created_unix_s=int(time.time()),
        )
        self._save_receipt(
            self._timeline_id,
            self._epoch,
            receipt,
        )
        return receipt
