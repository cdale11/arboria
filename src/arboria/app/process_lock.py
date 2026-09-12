"""OS-backed single-owner lock for the Arboria data directory."""

from __future__ import annotations

import fcntl
import os
import stat
from pathlib import Path
from types import TracebackType
from typing import TextIO

from .auth import data_dir


class ProcessLockError(RuntimeError):
    """Raised when another server already owns the data directory."""


class DataDirectoryLock:
    """Hold an advisory exclusive lock for the lifetime of a server process."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or data_dir()
        self.path = self.root / "server.lock"
        self._handle: TextIO | None = None

    def acquire(self) -> None:
        if self._handle is not None:
            return
        self.root.mkdir(parents=True, exist_ok=True)
        handle = self.path.open("a+", encoding="utf-8")
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            handle.close()
            raise ProcessLockError(
                f"Another Arboria server already owns data directory {self.root}"
            ) from exc
        handle.seek(0)
        handle.truncate()
        handle.write(f"pid={os.getpid()}\n")
        handle.flush()
        os.fsync(handle.fileno())
        self.path.chmod(stat.S_IRUSR | stat.S_IWUSR)
        self._handle = handle

    def release(self) -> None:
        if self._handle is None:
            return
        handle = self._handle
        self._handle = None
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()

    def __enter__(self) -> DataDirectoryLock:
        self.acquire()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.release()
