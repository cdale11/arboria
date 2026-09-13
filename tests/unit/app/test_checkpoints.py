import hashlib
import json
from pathlib import Path

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
    assert manifest["checkpoint_id"] == record.checkpoint_id
    assert manifest["sim_tick"] == 2
    state_path = checkpoint_dir / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["world_id"] == metadata.world_id
    assert state["loop"]["world_revision"] == 2
    assert manifest["files"][0]["sha256"] == hashlib.sha256(state_path.read_bytes()).hexdigest()
    assert record.manifest_hash == hashlib.sha256(
        (checkpoint_dir / "manifest.json").read_bytes()
    ).hexdigest()
