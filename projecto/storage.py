"""Document storage"""

import uuid
from pathlib import Path
from typing import Protocol, runtime_checkable

from projecto.config import settings


@runtime_checkable
class Storage(Protocol):
    """Abstract binary object store."""

    async def save(self, data: bytes) -> str:
        """Persist ``data`` and return an opaque storage key."""
        ...

    async def load(self, key: str) -> bytes:
        """Return the bytes previously stored under ``key``."""
        ...

    async def delete(self, key: str) -> None:
        """Remove the object stored under ``key`` (no-op if absent)."""
        ...


class LocalStorage:
    """Filesystem-backed storage rooted at a configurable directory."""

    def __init__(self, root: str | None = None) -> None:
        self._root = Path(root if root is not None else settings.storage_path)
        self._root.mkdir(parents=True, exist_ok=True)

    def _path_for(self, key: str) -> Path:
        # Keys are generated internally; guard against path traversal anyway.
        candidate = (self._root / key).resolve()
        if self._root.resolve() not in candidate.parents:
            raise ValueError("Invalid storage key.")
        return candidate

    async def save(self, data: bytes) -> str:
        """Write ``data`` to a new file and return its key."""
        key = uuid.uuid4().hex
        self._path_for(key).write_bytes(data)
        return key

    async def load(self, key: str) -> bytes:
        """Read and return the bytes stored under ``key``."""
        return self._path_for(key).read_bytes()

    async def delete(self, key: str) -> None:
        """Delete the file stored under ``key`` if it exists."""
        self._path_for(key).unlink(missing_ok=True)


def get_storage() -> Storage:
    """Return the configured storage backend."""
    return LocalStorage()
