"""Storage package — pluggable storage layer with factory function."""

from __future__ import annotations

from storage.base import StorageRepository
from storage.memory import InMemoryStorage

__all__ = ["StorageRepository", "InMemoryStorage", "get_storage"]

_instance: StorageRepository | None = None


def get_storage() -> StorageRepository:
    """Return the configured storage instance (in-memory by default)."""
    global _instance
    if _instance is None:
        _instance = InMemoryStorage()
    return _instance
