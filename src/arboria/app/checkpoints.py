"""Immutable checkpoint generation layout for the current metadata-only world."""

from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import time
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

from arboria.app.metadata import WorldMetadata
from arboria.sim.clock import ClockState
from arboria.sim.world_loop import WorldLoopState

CHECKPOINT_FORMAT_VERSION = 1
EXPORT_FORMAT_VERSION = 1
MAX_EXPORT_BYTES = 5_000_000


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
        nursery_protected_plants: list[int] | None = None,
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
            "nursery_protected_plants": (
                nursery_protected_plants if nursery_protected_plants is not None else []
            ),
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

    def export_checkpoint(self, checkpoint_id: str) -> bytes:
        manifest, state = self.load(checkpoint_id)
        metadata = {
            "format_version": EXPORT_FORMAT_VERSION,
            "kind": "arboria-current-domain-checkpoint",
            "checkpoint_id": checkpoint_id,
        }
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("arboria-export.json", self._canonical_json(metadata))
            archive.writestr("manifest.json", self._canonical_json(manifest))
            archive.writestr("state.json", self._canonical_json(state))
        payload = output.getvalue()
        if len(payload) > MAX_EXPORT_BYTES:
            raise ValueError("export archive is too large")
        return payload

    def import_checkpoint(self, payload: bytes) -> tuple[CheckpointRecord, dict[str, Any]]:
        if len(payload) > MAX_EXPORT_BYTES:
            raise ValueError("import archive is too large")
        try:
            with zipfile.ZipFile(io.BytesIO(payload), "r") as archive:
                names = archive.namelist()
                expected = {"arboria-export.json", "manifest.json", "state.json"}
                if set(names) != expected:
                    raise ValueError("export archive has unexpected entries")
                for info in archive.infolist():
                    if info.is_dir() or info.file_size > MAX_EXPORT_BYTES:
                        raise ValueError("export archive entry is invalid")
                metadata = json.loads(archive.read("arboria-export.json"))
                manifest = json.loads(archive.read("manifest.json"))
                state = json.loads(archive.read("state.json"))
        except zipfile.BadZipFile as exc:
            raise ValueError("invalid export archive") from exc
        if (
            not isinstance(metadata, dict)
            or metadata.get("format_version") != EXPORT_FORMAT_VERSION
        ):
            raise ValueError("unsupported export format")
        if metadata.get("kind") != "arboria-current-domain-checkpoint":
            raise ValueError("unsupported export kind")
        if not isinstance(manifest, dict) or not isinstance(state, dict):
            raise ValueError("export JSON must contain objects")
        checkpoint_id = str(uuid.uuid4())
        manifest = dict(manifest)
        manifest["checkpoint_id"] = checkpoint_id
        manifest["parent_checkpoint_id"] = None
        manifest["purpose"] = "import"
        state = dict(state)
        state["purpose"] = "import"
        tmp_dir = self.checkpoints_dir / f".{checkpoint_id}.tmp"
        final_dir = self.checkpoints_dir / checkpoint_id
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        tmp_dir.mkdir(mode=0o700)
        try:
            state_bytes = self._write_json(tmp_dir / "state.json", state)
            files = manifest.get("files")
            if not isinstance(files, list) or len(files) != 1 or not isinstance(files[0], dict):
                raise ValueError("checkpoint manifest must describe state.json")
            files[0] = dict(files[0])
            files[0]["relative_path"] = "state.json"
            files[0]["size_bytes"] = len(state_bytes)
            files[0]["sha256"] = hashlib.sha256(state_bytes).hexdigest()
            manifest["files"] = files
            manifest_bytes = self._write_json(tmp_dir / "manifest.json", manifest)
            manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()
            self._fsync_dir(tmp_dir)
            os.replace(tmp_dir, final_dir)
            self._fsync_dir(self.checkpoints_dir)
        except Exception:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            raise
        self.load(checkpoint_id)
        record = CheckpointRecord(
            checkpoint_id=checkpoint_id,
            parent_checkpoint_id=None,
            sim_tick=int(manifest["sim_tick"]),
            world_revision=int(manifest["world_revision"]),
            created_unix_s=int(time.time()),
            manifest_hash=manifest_hash,
            status="complete",
            purpose="manual",
        )
        return record, manifest

    def fallback_checkpoint_id(self, start_id: str) -> str | None:
        """Walk the parent chain for the first fully loadable checkpoint.

        Returns None when no ancestor (including the start) loads cleanly.
        Corrupt entries are skipped, never repaired or trusted.
        """
        seen: set[str] = set()
        current: str | None = start_id
        while current is not None and current not in seen:
            seen.add(current)
            try:
                self.load(current)
            except (FileNotFoundError, ValueError, OSError):
                current = self._parent_of(current)
                continue
            return current
        return None

    def _parent_of(self, checkpoint_id: str) -> str | None:
        try:
            UUID(checkpoint_id)
        except ValueError:
            return None
        manifest_path = self.checkpoints_dir / checkpoint_id / "manifest.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (FileNotFoundError, ValueError, OSError, UnicodeDecodeError):
            return None
        if not isinstance(manifest, dict):
            return None
        parent = manifest.get("parent_checkpoint_id")
        return parent if isinstance(parent, str) else None

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
    def _canonical_json(payload: dict[str, Any]) -> str:
        return json.dumps(payload, sort_keys=True, indent=2)

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> bytes:
        data = CheckpointWriter._canonical_json(payload).encode("utf-8")
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
