from pathlib import Path

import pytest

from arboria.app.process_lock import DataDirectoryLock, ProcessLockError


def test_data_directory_lock_blocks_second_owner(tmp_path: Path) -> None:
    first = DataDirectoryLock(tmp_path)
    second = DataDirectoryLock(tmp_path)

    first.acquire()
    try:
        with pytest.raises(ProcessLockError):
            second.acquire()
    finally:
        first.release()


def test_data_directory_lock_releases_for_next_owner(tmp_path: Path) -> None:
    first = DataDirectoryLock(tmp_path)
    second = DataDirectoryLock(tmp_path)

    first.acquire()
    first.release()

    second.acquire()
    try:
        assert (tmp_path / "server.lock").read_text(encoding="utf-8").startswith("pid=")
    finally:
        second.release()
