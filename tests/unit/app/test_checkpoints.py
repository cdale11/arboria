import hashlib
import json
from pathlib import Path

import pytest
from pytest import MonkeyPatch

from arboria.app.checkpoints import CHECKPOINT_FORMAT_VERSION, CheckpointWriter
from arboria.app.metadata import MetadataStore
from arboria.sim.clock import ClockState
from arboria.sim.world_loop import WorldLoopState


def test_checkpoint_writer_creates_immutable_manifest_and_state(tmp_path: Path) -> None:
    store = MetadataStore(tmp_path)
    metadata = store.initialize_for_process_start()
    writer = CheckpointWriter(tmp_path)
    clock = ClockState(sim_time_seconds=600.0, speed=48.0, paused=False)
    loop = WorldLoopState(sim_tick=2, world_revision=2, consumed_sim_time_seconds=600.0)

    record, manifest = writer.create(
        metadata=metadata,
        clock=clock,
        loop=loop,
        parent_checkpoint_id=None,
        receipt_count=0,
    )

    checkpoint_dir = tmp_path / "checkpoints" / record.checkpoint_id
    assert checkpoint_dir.is_dir()
    assert not (tmp_path / "checkpoints" / f".{record.checkpoint_id}.tmp").exists()
    assert manifest["format_version"] == CHECKPOINT_FORMAT_VERSION
    assert manifest["purpose"] == "manual"
    assert manifest["checkpoint_id"] == record.checkpoint_id
    assert manifest["sim_tick"] == 2
    state_path = checkpoint_dir / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["world_id"] == metadata.world_id
    assert state["purpose"] == "manual"
    assert state["loop"]["world_revision"] == 2
    assert manifest["files"][0]["sha256"] == hashlib.sha256(state_path.read_bytes()).hexdigest()
    assert record.manifest_hash == hashlib.sha256(
        (checkpoint_dir / "manifest.json").read_bytes()
    ).hexdigest()


def test_checkpoint_reader_rejects_corrupt_state(tmp_path: Path) -> None:
    store = MetadataStore(tmp_path)
    metadata = store.initialize_for_process_start()
    writer = CheckpointWriter(tmp_path)
    record, _ = writer.create(
        metadata=metadata,
        clock=ClockState(sim_time_seconds=0.0, speed=48.0, paused=False),
        loop=WorldLoopState(0, 0, 0.0),
        parent_checkpoint_id=None,
        receipt_count=0,
    )
    (tmp_path / "checkpoints" / record.checkpoint_id / "state.json").write_text(
        "{}", encoding="utf-8"
    )

    try:
        writer.load(record.checkpoint_id)
        raise AssertionError("corrupt checkpoint should be rejected")
    except ValueError as exc:
        assert "mismatch" in str(exc)


def test_checkpoint_cleanup_removes_only_interrupted_generations(tmp_path: Path) -> None:
    writer = CheckpointWriter(tmp_path)
    complete = tmp_path / "checkpoints" / "complete"
    interrupted = tmp_path / "checkpoints" / ".abc.tmp"
    complete.mkdir(parents=True)
    interrupted.mkdir()
    (interrupted / "state.json").write_text("{}", encoding="utf-8")

    removed = writer.cleanup_interrupted_generations()

    assert removed == 1
    assert complete.is_dir()
    assert not interrupted.exists()


def make_writer(tmp_path: Path) -> tuple[MetadataStore, CheckpointWriter]:
    store = MetadataStore(tmp_path)
    metadata = store.initialize_for_process_start()
    writer = CheckpointWriter(tmp_path)
    assert metadata is not None
    return store, writer


def create_chain(tmp_path: Path) -> tuple[CheckpointWriter, str, str]:
    store = MetadataStore(tmp_path)
    metadata = store.initialize_for_process_start()
    writer = CheckpointWriter(tmp_path)
    clock = ClockState(sim_time_seconds=0.0, speed=48.0, paused=False)
    loop = WorldLoopState(0, 0, 0.0)
    parent, _ = writer.create(
        metadata=metadata,
        clock=clock,
        loop=loop,
        parent_checkpoint_id=None,
        receipt_count=0,
    )
    child, _ = writer.create(
        metadata=metadata,
        clock=clock,
        loop=loop,
        parent_checkpoint_id=parent.checkpoint_id,
        receipt_count=0,
    )
    return writer, parent.checkpoint_id, child.checkpoint_id


def corrupt_state(tmp_path: Path, checkpoint_id: str) -> None:
    (tmp_path / "checkpoints" / checkpoint_id / "state.json").write_text(
        "{}", encoding="utf-8"
    )


def test_atomic_save_failure_leaves_no_final_dir_and_cleans_up(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    store, writer = make_writer(tmp_path)
    calls = {"count": 0}
    original = CheckpointWriter._write_json

    def failing_write(path: Path, payload: dict[str, object]) -> bytes:
        calls["count"] += 1
        if calls["count"] == 2:
            raise OSError("injected disk failure")
        return original(path, payload)

    monkeypatch.setattr(CheckpointWriter, "_write_json", staticmethod(failing_write))
    metadata = store.load()

    with pytest.raises(OSError, match="injected disk failure"):
        writer.create(
            metadata=metadata,
            clock=ClockState(sim_time_seconds=0.0, speed=48.0, paused=False),
            loop=WorldLoopState(0, 0, 0.0),
            parent_checkpoint_id=None,
            receipt_count=0,
        )

    leftovers = [
        path
        for path in (tmp_path / "checkpoints").iterdir()
        if not path.name.startswith(".")
    ]
    assert leftovers == []
    assert store.load().active_checkpoint_id is None

    removed = writer.cleanup_interrupted_generations()
    assert removed == 1

    monkeypatch.undo()
    record, _ = writer.create(
        metadata=store.load(),
        clock=ClockState(sim_time_seconds=0.0, speed=48.0, paused=False),
        loop=WorldLoopState(0, 0, 0.0),
        parent_checkpoint_id=None,
        receipt_count=0,
    )
    assert (tmp_path / "checkpoints" / record.checkpoint_id).is_dir()


def test_fallback_walks_parent_chain_past_corrupt_generations(
    tmp_path: Path,
) -> None:
    writer, parent_id, child_id = create_chain(tmp_path)

    assert writer.fallback_checkpoint_id(child_id) == child_id
    corrupt_state(tmp_path, child_id)
    assert writer.fallback_checkpoint_id(child_id) == parent_id
    corrupt_state(tmp_path, parent_id)
    assert writer.fallback_checkpoint_id(child_id) is None


def test_fallback_rejects_unknown_and_malformed_ids(tmp_path: Path) -> None:
    writer = CheckpointWriter(tmp_path)

    assert writer.fallback_checkpoint_id("00000000-0000-0000-0000-000000000000") is None
    assert writer.fallback_checkpoint_id("not-a-uuid") is None
