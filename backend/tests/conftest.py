"""Pytest configuration and fixtures for backend tests."""

import json
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from src.config import Settings
from src.main import app
from src.services.storage import LocalFileStorageAdapter, StorageAdapter


@pytest.fixture
def sample_services() -> list[dict]:
    """Sample service data for testing."""
    return [
        {
            "service": "Azure Virtual Machines",
            "category": "Compute",
            "description": "On-demand, scalable virtual machines for Windows and Linux workloads.",
        },
        {
            "service": "Azure App Service",
            "category": "App Platform",
            "description": "Fully managed platform for web apps and APIs.",
        },
        {
            "service": "Azure SQL Database",
            "category": "Databases",
            "description": "Managed relational database service compatible with SQL Server.",
        },
    ]


@pytest.fixture
def temp_services_file(sample_services: list[dict]) -> Generator[Path, None, None]:
    """Create a temporary services.json file for testing.

    Yields:
        Path to the temporary file.
    """
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        delete=False,
        encoding="utf-8",
    ) as f:
        json.dump({"services": sample_services}, f)
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def empty_temp_file() -> Generator[Path, None, None]:
    """Create an empty temporary file path (file doesn't exist).

    Yields:
        Path to a non-existent temporary file.
    """
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        delete=True,
    ) as f:
        temp_path = Path(f.name)

    # File is deleted, so we just return the path
    yield temp_path

    # Cleanup if file was created during test
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def storage_adapter(temp_services_file: Path) -> LocalFileStorageAdapter:
    """Create a LocalFileStorageAdapter with test data.

    Args:
        temp_services_file: Path to temporary services file.

    Returns:
        Configured storage adapter.
    """
    return LocalFileStorageAdapter(str(temp_services_file))


@pytest.fixture
def empty_storage_adapter(empty_temp_file: Path) -> LocalFileStorageAdapter:
    """Create a LocalFileStorageAdapter with no data.

    Args:
        empty_temp_file: Path to non-existent file.

    Returns:
        Storage adapter that will return empty results.
    """
    return LocalFileStorageAdapter(str(empty_temp_file))


@pytest.fixture
def test_settings(temp_services_file: Path) -> Settings:
    """Create test settings with local storage.

    Args:
        temp_services_file: Path to temporary services file.

    Returns:
        Settings configured for testing.
    """
    return Settings(
        storage_type="local",
        local_data_path=str(temp_services_file),
        debug=True,
    )


@pytest.fixture
def client() -> TestClient:
    """Create a FastAPI test client.

    Returns:
        TestClient for the FastAPI app.
    """
    return TestClient(app)
