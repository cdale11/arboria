"""SQLite metadata for the single persistent Arboria world."""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

from arboria.app.commands import Receipt
from arboria.sim.clock import ClockState

from .auth import data_dir

METADATA_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class WorldMetadata:
    world_id: str
    timeline_id: str
    schema_version: int
    request_epoch: int
    clock: ClockState


class MetadataStore:
    """Own the small durable metadata database before full checkpoints exist."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or data_dir()
        self.path = self.root / "world.sqlite3"

    def initialize_for_process_start(self) -> WorldMetadata:
        self.root.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            self._create_schema(connection)
            row = connection.execute(
                "SELECT world_id, schema_version, request_epoch, clock_sim_time_seconds, "
                "clock_speed, clock_paused FROM worlds WHERE id = 1"
            ).fetchone()
            next_timeline = str(uuid.uuid4())
            now = int(time.time())
            if row is None:
                world_id = str(uuid.uuid4())
                epoch = 1
                connection.execute(
                    "INSERT INTO worlds (id, world_id, timeline_id, schema_version, "
                    "request_epoch, created_at, updated_at, clock_sim_time_seconds, "
                    "clock_speed, clock_paused) "
                    "VALUES (1, ?, ?, ?, ?, ?, ?, 0.0, 48.0, 0)",
                    (
                        world_id,
                        next_timeline,
                        METADATA_SCHEMA_VERSION,
                        epoch,
                        now,
                        now,
                    ),
                )
                clock = ClockState(0.0, 48.0, False)
            else:
                world_id = str(row["world_id"])
                epoch = int(row["request_epoch"]) + 1
                connection.execute(
                    "UPDATE worlds SET timeline_id = ?, request_epoch = ?, updated_at = ? "
                    "WHERE id = 1",
                    (next_timeline, epoch, now),
                )
                clock = ClockState(
                    sim_time_seconds=float(row["clock_sim_time_seconds"]),
                    speed=float(row["clock_speed"]),
                    paused=bool(row["clock_paused"]),
                )
            connection.commit()
            return WorldMetadata(world_id, next_timeline, METADATA_SCHEMA_VERSION, epoch, clock)

    def save_clock(self, clock: ClockState) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE worlds SET clock_sim_time_seconds = ?, clock_speed = ?, "
                "clock_paused = ?, updated_at = ? WHERE id = 1",
                (clock.sim_time_seconds, clock.speed, int(clock.paused), int(time.time())),
            )
            connection.commit()

    def load(self) -> WorldMetadata:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT world_id, timeline_id, schema_version, request_epoch, "
                "clock_sim_time_seconds, clock_speed, clock_paused FROM worlds WHERE id = 1"
            ).fetchone()
            if row is None:
                raise RuntimeError("World metadata has not been initialized.")
            return WorldMetadata(
                world_id=str(row["world_id"]),
                timeline_id=str(row["timeline_id"]),
                schema_version=int(row["schema_version"]),
                request_epoch=int(row["request_epoch"]),
                clock=ClockState(
                    sim_time_seconds=float(row["clock_sim_time_seconds"]),
                    speed=float(row["clock_speed"]),
                    paused=bool(row["clock_paused"]),
                ),
            )

    def find_receipt(
        self, timeline_id: str, request_epoch: int, command_id: str
    ) -> Receipt | None:
        with self._connect() as connection:
            self._create_schema(connection)
            row = connection.execute(
                "SELECT actor, kind, status, reason, result_json, created_unix_s "
                "FROM command_receipts WHERE timeline_id = ? AND request_epoch = ? "
                "AND command_id = ?",
                (timeline_id, request_epoch, command_id),
            ).fetchone()
            if row is None:
                return None
            result = json.loads(row["result_json"]) if row["result_json"] is not None else None
            if result is not None and not isinstance(result, dict):
                raise RuntimeError("Invalid command receipt result payload.")
            return Receipt(
                command_id=command_id,
                actor=str(row["actor"]),
                kind=str(row["kind"]),
                status=str(row["status"]),
                reason=row["reason"],
                result=result,
                created_unix_s=int(row["created_unix_s"]),
            )

    def save_receipt(self, timeline_id: str, request_epoch: int, receipt: Receipt) -> None:
        with self._connect() as connection:
            self._create_schema(connection)
            connection.execute(
                "INSERT INTO command_receipts (timeline_id, request_epoch, command_id, "
                "actor, kind, status, reason, result_json, created_unix_s) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    timeline_id,
                    request_epoch,
                    receipt.command_id,
                    receipt.actor,
                    receipt.kind,
                    receipt.status,
                    receipt.reason,
                    (
                        json.dumps(receipt.result, sort_keys=True)
                        if receipt.result is not None
                        else None
                    ),
                    receipt.created_unix_s,
                ),
            )
            connection.commit()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA synchronous = FULL")
        return connection

    @staticmethod
    def _create_schema(connection: sqlite3.Connection) -> None:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS worlds ("
            "id INTEGER PRIMARY KEY CHECK (id = 1), "
            "world_id TEXT NOT NULL UNIQUE, "
            "timeline_id TEXT NOT NULL, "
            "schema_version INTEGER NOT NULL, "
            "request_epoch INTEGER NOT NULL DEFAULT 1 CHECK (request_epoch >= 1), "
            "active_checkpoint_id TEXT, "
            "created_at INTEGER NOT NULL, "
            "updated_at INTEGER NOT NULL, "
            "clock_sim_time_seconds REAL NOT NULL CHECK (clock_sim_time_seconds >= 0), "
            "clock_speed REAL NOT NULL CHECK (clock_speed >= 1 AND clock_speed <= 144), "
            "clock_paused INTEGER NOT NULL CHECK (clock_paused IN (0, 1))"
            ")"
        )
        columns = {
            str(row["name"])
            for row in connection.execute("PRAGMA table_info(worlds)").fetchall()
        }
        if "request_epoch" not in columns:
            connection.execute(
                "ALTER TABLE worlds ADD COLUMN request_epoch INTEGER NOT NULL DEFAULT 1 "
                "CHECK (request_epoch >= 1)"
            )
        connection.execute(
            "CREATE TABLE IF NOT EXISTS command_receipts ("
            "timeline_id TEXT NOT NULL, "
            "request_epoch INTEGER NOT NULL CHECK (request_epoch >= 1), "
            "command_id TEXT NOT NULL, "
            "actor TEXT NOT NULL, "
            "kind TEXT NOT NULL, "
            "status TEXT NOT NULL CHECK (status IN ('applied', 'queued', 'rejected')), "
            "reason TEXT, "
            "result_json TEXT, "
            "created_unix_s INTEGER NOT NULL, "
            "PRIMARY KEY (timeline_id, request_epoch, command_id)"
            ")"
        )
