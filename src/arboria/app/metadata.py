"""SQLite metadata for the single persistent Arboria world."""

from __future__ import annotations

import sqlite3
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

from arboria.sim.clock import ClockState

from .auth import data_dir

METADATA_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class WorldMetadata:
    world_id: str
    timeline_id: str
    schema_version: int
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
                "SELECT world_id, schema_version, clock_sim_time_seconds, clock_speed, "
                "clock_paused FROM worlds WHERE id = 1"
            ).fetchone()
            next_timeline = str(uuid.uuid4())
            now = int(time.time())
            if row is None:
                world_id = str(uuid.uuid4())
                connection.execute(
                    "INSERT INTO worlds (id, world_id, timeline_id, schema_version, "
                    "created_at, updated_at, clock_sim_time_seconds, clock_speed, clock_paused) "
                    "VALUES (1, ?, ?, ?, ?, ?, 0.0, 48.0, 0)",
                    (world_id, next_timeline, METADATA_SCHEMA_VERSION, now, now),
                )
                clock = ClockState(0.0, 48.0, False)
            else:
                world_id = str(row["world_id"])
                connection.execute(
                    "UPDATE worlds SET timeline_id = ?, updated_at = ? WHERE id = 1",
                    (next_timeline, now),
                )
                clock = ClockState(
                    sim_time_seconds=float(row["clock_sim_time_seconds"]),
                    speed=float(row["clock_speed"]),
                    paused=bool(row["clock_paused"]),
                )
            connection.commit()
            return WorldMetadata(world_id, next_timeline, METADATA_SCHEMA_VERSION, clock)

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
                "SELECT world_id, timeline_id, schema_version, clock_sim_time_seconds, "
                "clock_speed, clock_paused FROM worlds WHERE id = 1"
            ).fetchone()
            if row is None:
                raise RuntimeError("World metadata has not been initialized.")
            return WorldMetadata(
                world_id=str(row["world_id"]),
                timeline_id=str(row["timeline_id"]),
                schema_version=int(row["schema_version"]),
                clock=ClockState(
                    sim_time_seconds=float(row["clock_sim_time_seconds"]),
                    speed=float(row["clock_speed"]),
                    paused=bool(row["clock_paused"]),
                ),
            )

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
            "active_checkpoint_id TEXT, "
            "created_at INTEGER NOT NULL, "
            "updated_at INTEGER NOT NULL, "
            "clock_sim_time_seconds REAL NOT NULL CHECK (clock_sim_time_seconds >= 0), "
            "clock_speed REAL NOT NULL CHECK (clock_speed >= 1 AND clock_speed <= 144), "
            "clock_paused INTEGER NOT NULL CHECK (clock_paused IN (0, 1))"
            ")"
        )
