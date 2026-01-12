"""FastAPI dependencies for dependency injection."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from src.config import Settings, get_settings
from src.services.storage import StorageAdapter, get_storage_adapter


# Cache the storage adapter at module level
_storage_adapter: StorageAdapter | None = None


def get_storage(settings: Settings = Depends(get_settings)) -> StorageAdapter:
    """Get cached storage adapter instance.

    This is cached to ensure a single storage adapter instance
    is reused across requests.

    Args:
        settings: Application settings.

    Returns:
        StorageAdapter: Configured storage adapter.
    """
    global _storage_adapter
    if _storage_adapter is None:
        _storage_adapter = get_storage_adapter(settings)
    return _storage_adapter


# Type aliases for cleaner dependency injection
SettingsDep = Annotated[Settings, Depends(get_settings)]
StorageDep = Annotated[StorageAdapter, Depends(get_storage)]
