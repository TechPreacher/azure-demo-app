"""FastAPI dependencies for dependency injection."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from src.config import Settings, get_settings
from src.services.storage import StorageAdapter, get_storage_adapter


@lru_cache
def get_storage(settings: Settings = Depends(get_settings)) -> StorageAdapter:
    """Get cached storage adapter instance.

    This is cached to ensure a single storage adapter instance
    is reused across requests.

    Args:
        settings: Application settings.

    Returns:
        StorageAdapter: Configured storage adapter.
    """
    return get_storage_adapter(settings)


# Type aliases for cleaner dependency injection
SettingsDep = Annotated[Settings, Depends(get_settings)]
StorageDep = Annotated[StorageAdapter, Depends(get_storage)]
