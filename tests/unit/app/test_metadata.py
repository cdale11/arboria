import sqlite3
from pathlib import Path

from arboria.app.commands import Receipt
from arboria.app.metadata import METADATA_SCHEMA_VERSION, MetadataStore
from arboria.sim.clock import ClockState
from arboria.sim.world_loop import WorldLoopState


def test_metadata_store_creates_world_and_rotates_timeline(tmp_path: Path) -> None:
    store = MetadataStore(tmp_path)

    first = store.initialize_for_process_start()
    second = store.initialize_for_process_start()

    assert first.world_id == second.world_id
    assert first.timeline_id != second.timeline_id
    assert second.request_epoch == first.request_epoch + 1
    assert second.schema_version == METADATA_SCHEMA_VERSION
    assert (tmp_path / "world.sqlite3").is_file()


def test_metadata_store_persists_clock_state(tmp_path: Path) -> None:
    store = MetadataStore(tmp_path)
    store.initialize_for_process_start()

    store.save_clock(ClockState(sim_time_seconds=1234.5, speed=12.0, paused=True))

    loaded = store.load()

    assert loaded.clock == ClockState(sim_time_seconds=1234.5, speed=12.0, paused=True)


def test_metadata_store_persists_world_loop_state(tmp_path: Path) -> None:
    store = MetadataStore(tmp_path)
    store.initialize_for_process_start()

    store.save_loop(WorldLoopState(sim_tick=3, world_revision=3, consumed_sim_time_seconds=900.0))

    loaded = store.load()

    assert loaded.loop == WorldLoopState(
        sim_tick=3,
        world_revision=3,
        consumed_sim_time_seconds=900.0,
    )


def test_metadata_store_persists_command_receipts(tmp_path: Path) -> None:
    store = MetadataStore(tmp_path)
    metadata = store.initialize_for_process_start()

    receipt = Receipt(
        command_id="00000000-0000-0000-0000-000000000001",
        actor="player",
        kind="clock.pause",
        status="applied",
        reason=None,
        result={"clock": {"paused": True}},
        created_unix_s=123,
    )
    store.save_receipt(
        metadata.timeline_id,
        metadata.request_epoch,
        receipt,
    )

    loaded = store.find_receipt(
        metadata.timeline_id,
        metadata.request_epoch,
        receipt.command_id,
    )

    assert loaded == receipt


def test_metadata_store_registers_active_checkpoint(tmp_path: Path) -> None:
    store = MetadataStore(tmp_path)
    store.initialize_for_process_start()

    store.register_checkpoint(
        checkpoint_id="checkpoint-a",
        parent_checkpoint_id=None,
        sim_tick=1,
        world_revision=1,
        created_unix_s=123,
        manifest_hash="abc123",
        status="complete",
    )

    loaded = store.load()

    assert loaded.active_checkpoint_id == "checkpoint-a"


def test_metadata_store_marks_last_autosave(tmp_path: Path) -> None:
    store = MetadataStore(tmp_path)
    store.initialize_for_process_start()
    store.register_checkpoint(
        checkpoint_id="checkpoint-a",
        parent_checkpoint_id=None,
        sim_tick=1,
        world_revision=1,
        created_unix_s=123,
        manifest_hash="abc123",
        status="complete",
        purpose="autosave",
    )

    store.mark_autosave("checkpoint-a", 123)
    loaded = store.load()

    assert loaded.active_checkpoint_id == "checkpoint-a"
    assert loaded.last_autosave_unix_s == 123


def test_metadata_store_names_and_lists_snapshots(tmp_path: Path) -> None:
    store = MetadataStore(tmp_path)
    store.initialize_for_process_start()
    store.register_checkpoint(
        checkpoint_id="checkpoint-a",
        parent_checkpoint_id=None,
        sim_tick=1,
        world_revision=1,
        created_unix_s=123,
        manifest_hash="abc123",
        status="complete",
    )

    store.name_snapshot(
        name="Morning save",
        checkpoint_id="checkpoint-a",
        created_unix_s=123,
        protected=True,
    )

    snapshots = store.list_snapshots()

    assert len(snapshots) == 1
    assert snapshots[0].name == "Morning save"
    assert snapshots[0].checkpoint_id == "checkpoint-a"
    assert snapshots[0].protected is True


def test_metadata_store_enables_durable_sqlite_settings(tmp_path: Path) -> None:
    store = MetadataStore(tmp_path)
    store.initialize_for_process_start()

    with sqlite3.connect(tmp_path / "world.sqlite3") as connection:
        journal_mode = connection.execute("PRAGMA journal_mode").fetchone()[0]
        synchronous = connection.execute("PRAGMA synchronous").fetchone()[0]

    assert journal_mode == "wal"
    assert synchronous == 2
