"""Immutable checkpoint generation layout for the current metadata-only world."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

from arboria.app.metadata import WorldMetadata
from arboria.sim.clock import ClockState
from arboria.sim.world_loop import WorldLoopState

CHECKPOINT_FORMAT_VERSION = 1


@dataclass(frozen=True)
class CheckpointRecord:
    checkpoint_id: str
    parent_checkpoint_id: str | None
    sim_tick: int
    world_revision: int
    created_unix_s: int
    manifest_hash: str
    status: str
    purpose: str


class CheckpointWriter:
    """Create immutable checkpoint directories with a manifest and state payload."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.checkpoints_dir = root / "checkpoints"

    def create(
        self,
        *,
        metadata: WorldMetadata,
        clock: ClockState,
        loop: WorldLoopState,
        parent_checkpoint_id: str | None,
        receipt_count: int,
        purpose: str = "manual",
        nursery_organs: list[dict[str, Any]] | None = None,
        nursery_schema_version: int = 1,
        nursery_zones: list[dict[str, Any]] | None = None,
        nursery_nutrient_zones: list[dict[str, Any]] | None = None,
        nursery_species: list[dict[str, Any]] | None = None,
        nursery_economy: dict[str, Any] | None = None,
        nursery_reservoir_kg: float = 0.0,
    ) -> tuple[CheckpointRecord, dict[str, Any]]:
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        checkpoint_id = str(uuid.uuid4())
        created = int(time.time())
        tmp_dir = self.checkpoints_dir / f".{checkpoint_id}.tmp"
        final_dir = self.checkpoints_dir / checkpoint_id
        tmp_dir.mkdir(mode=0o700)
        state = {
            "world_id": metadata.world_id,
            "timeline_id": metadata.timeline_id,
            "request_epoch": metadata.request_epoch,
            "purpose": purpose,
            "schema_version": metadata.schema_version,
            "clock": {
                "sim_time_seconds": clock.sim_time_seconds,
                "speed": clock.speed,
                "paused": clock.paused,
            },
            "loop": {
                "sim_tick": loop.sim_tick,
                "world_revision": loop.world_revision,
                "consumed_sim_time_seconds": loop.consumed_sim_time_seconds,
            },
            "receipt_count": receipt_count,
            "nursery_schema_version": nursery_schema_version,
            "nursery_organs": nursery_organs if nursery_organs is not None else [],
            "nursery_zones": nursery_zones if nursery_zones is not None else [],
            "nursery_nutrient_zones": (
                nursery_nutrient_zones if nursery_nutrient_zones is not None else []
            ),
            "nursery_species": nursery_species if nursery_species is not None else [],
            "nursery_economy": nursery_economy if nursery_economy is not None else {},
            "nursery_reservoir_kg": nursery_reservoir_kg,
        }
        state_bytes = self._write_json(tmp_dir / "state.json", state)
        state_hash = hashlib.sha256(state_bytes).hexdigest()
        manifest = {
            "format_version": CHECKPOINT_FORMAT_VERSION,
            "world_id": metadata.world_id,
            "timeline_id": metadata.timeline_id,
            "checkpoint_id": checkpoint_id,
            "parent_checkpoint_id": parent_checkpoint_id,
            "sim_tick": loop.sim_tick,
            "sim_time_seconds": clock.sim_time_seconds,
            "speed": clock.speed,
            "paused": clock.paused,
            "world_revision": loop.world_revision,
            "created_unix_s": created,
            "schema_version": metadata.schema_version,
            "request_epoch": metadata.request_epoch,
            "purpose": purpose,
            "files": [
                {
                    "relative_path": "state.json",
                    "size_bytes": len(state_bytes),
                    "sha256": state_hash,
                    "domain_schema_version": metadata.schema_version,
                }
            ],
        }
        manifest_bytes = self._write_json(tmp_dir / "manifest.json", manifest)
        manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()
        self._fsync_dir(tmp_dir)
        os.replace(tmp_dir, final_dir)
        self._fsync_dir(self.checkpoints_dir)
        record = CheckpointRecord(
            checkpoint_id=checkpoint_id,
            parent_checkpoint_id=parent_checkpoint_id,
            sim_tick=loop.sim_tick,
            world_revision=loop.world_revision,
            created_unix_s=created,
            manifest_hash=manifest_hash,
            status="complete",
            purpose=purpose,
        )
        return record, manifest

    def load(self, checkpoint_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
        try:
            UUID(checkpoint_id)
        except ValueError as exc:
            raise ValueError("checkpoint_id must be a UUID") from exc
        checkpoint_dir = self.checkpoints_dir / checkpoint_id
        manifest_path = checkpoint_dir / "manifest.json"
        state_path = checkpoint_dir / "state.json"
        if not manifest_path.is_file() or not state_path.is_file():
            raise FileNotFoundError("checkpoint files are missing")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or not isinstance(state, dict):
            raise ValueError("checkpoint JSON must contain objects")
        if manifest.get("checkpoint_id") != checkpoint_id:
            raise ValueError("checkpoint manifest ID mismatch")
        files = manifest.get("files")
        if not isinstance(files, list) or len(files) != 1:
            raise ValueError("checkpoint manifest must describe state.json")
        file_record = files[0]
        if not isinstance(file_record, dict) or file_record.get("relative_path") != "state.json":
            raise ValueError("checkpoint manifest file record is invalid")
        state_bytes = state_path.read_bytes()
        if int(file_record.get("size_bytes", -1)) != len(state_bytes):
            raise ValueError("checkpoint state size mismatch")
        if file_record.get("sha256") != hashlib.sha256(state_bytes).hexdigest():
            raise ValueError("checkpoint state hash mismatch")
        return manifest, state

    def cleanup_interrupted_generations(self) -> int:
        if not self.checkpoints_dir.exists():
            return 0
        removed = 0
        for path in self.checkpoints_dir.iterdir():
            if path.is_dir() and path.name.startswith(".") and path.name.endswith(".tmp"):
                shutil.rmtree(path)
                removed += 1
        return removed

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> bytes:
        data = json.dumps(payload, sort_keys=True, indent=2).encode("utf-8")
        with path.open("wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        path.chmod(0o600)
        return data

    @staticmethod
    def _fsync_dir(path: Path) -> None:
        fd = os.open(path, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
