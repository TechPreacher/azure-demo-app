"""Unit tests for storage service operations.

Tests the StorageAdapter implementations for CRUD operations.
"""

import tempfile
from pathlib import Path

import pytest

from src.models.service import Service, ServiceCreate
from src.services.storage import (
    DuplicateServiceError,
    LocalFileStorageAdapter,
    ServiceNotFoundError,
    StorageError,
)


class TestLocalFileStorageAdapterListServices:
    """Unit tests for LocalFileStorageAdapter.list_services()."""

    def test_list_services_returns_all_services(
        self, storage_adapter: LocalFileStorageAdapter, sample_services: list[dict]
    ) -> None:
        """Test that list_services returns all services when no filters."""
        result = storage_adapter.list_services()

        assert len(result) == len(sample_services)
        assert all(isinstance(svc, Service) for svc in result)

    def test_list_services_returns_empty_list_when_no_data(
        self, empty_storage_adapter: LocalFileStorageAdapter
    ) -> None:
        """Test that list_services returns empty list when file doesn't exist."""
        result = empty_storage_adapter.list_services()

        assert result == []

    def test_list_services_filters_by_category(
        self, storage_adapter: LocalFileStorageAdapter
    ) -> None:
        """Test that list_services correctly filters by category."""
        result = storage_adapter.list_services(category="Compute")

        assert len(result) == 1
        assert result[0].service == "Azure Virtual Machines"
        assert result[0].category == "Compute"

    def test_list_services_category_filter_is_case_insensitive(
        self, storage_adapter: LocalFileStorageAdapter
    ) -> None:
        """Test that category filter is case-insensitive."""
        result_lower = storage_adapter.list_services(category="compute")
        result_upper = storage_adapter.list_services(category="COMPUTE")

        assert len(result_lower) == 1
        assert len(result_upper) == 1
        assert result_lower[0].service == result_upper[0].service

    def test_list_services_filters_by_search_in_name(
        self, storage_adapter: LocalFileStorageAdapter
    ) -> None:
        """Test that search filter matches service names."""
        result = storage_adapter.list_services(search="Virtual")

        assert len(result) == 1
        assert result[0].service == "Azure Virtual Machines"

    def test_list_services_filters_by_search_in_description(
        self, storage_adapter: LocalFileStorageAdapter
    ) -> None:
        """Test that search filter matches descriptions."""
        result = storage_adapter.list_services(search="fully managed")

        assert len(result) == 1
        assert result[0].service == "Azure App Service"

    def test_list_services_search_is_case_insensitive(
        self, storage_adapter: LocalFileStorageAdapter
    ) -> None:
        """Test that search filter is case-insensitive."""
        result = storage_adapter.list_services(search="SQL")

        assert len(result) == 1
        assert result[0].service == "Azure SQL Database"

    def test_list_services_combines_category_and_search_filters(
        self, storage_adapter: LocalFileStorageAdapter
    ) -> None:
        """Test that category and search filters can be combined."""
        result = storage_adapter.list_services(
            category="Databases",
            search="managed",
        )

        assert len(result) == 1
        assert result[0].service == "Azure SQL Database"

    def test_list_services_returns_empty_when_no_matches(
        self, storage_adapter: LocalFileStorageAdapter
    ) -> None:
        """Test that list_services returns empty list when no matches."""
        result = storage_adapter.list_services(category="Nonexistent")

        assert result == []

    def test_list_services_handles_invalid_json(self) -> None:
        """Test that list_services raises StorageError on invalid JSON."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write("invalid json content")
            temp_path = Path(f.name)

        try:
            adapter = LocalFileStorageAdapter(str(temp_path))
            with pytest.raises(StorageError, match="Invalid JSON"):
                adapter.list_services()
        finally:
            temp_path.unlink()


class TestLocalFileStorageAdapterGetService:
    """Unit tests for LocalFileStorageAdapter.get_service()."""

    def test_get_service_returns_service_by_name(
        self, storage_adapter: LocalFileStorageAdapter
    ) -> None:
        """Test that get_service returns correct service by exact name."""
        result = storage_adapter.get_service("Azure Virtual Machines")

        assert isinstance(result, Service)
        assert result.service == "Azure Virtual Machines"
        assert result.category == "Compute"

    def test_get_service_raises_not_found_for_missing_service(
        self, storage_adapter: LocalFileStorageAdapter
    ) -> None:
        """Test that get_service raises ServiceNotFoundError for missing service."""
        with pytest.raises(ServiceNotFoundError, match="Service not found"):
            storage_adapter.get_service("Nonexistent Service")

    def test_get_service_name_is_case_sensitive(
        self, storage_adapter: LocalFileStorageAdapter
    ) -> None:
        """Test that service name lookup is case-sensitive."""
        with pytest.raises(ServiceNotFoundError):
            storage_adapter.get_service("azure virtual machines")


class TestLocalFileStorageAdapterCreateService:
    """Unit tests for LocalFileStorageAdapter.create_service()."""

    def test_create_service_adds_new_service(
        self, storage_adapter: LocalFileStorageAdapter
    ) -> None:
        """Test that create_service adds a new service to storage."""
        new_service = ServiceCreate(
            service="Azure Container Apps",
            category="Containers",
            description="Fully managed serverless container service.",
        )

        result = storage_adapter.create_service(new_service)

        assert isinstance(result, Service)
        assert result.service == "Azure Container Apps"
        assert result.category == "Containers"
        assert result.description == "Fully managed serverless container service."

    def test_create_service_persists_to_storage(
        self, storage_adapter: LocalFileStorageAdapter
    ) -> None:
        """Test that created service can be retrieved."""
        new_service = ServiceCreate(
            service="Azure Container Apps",
            category="Containers",
            description="Fully managed serverless container service.",
        )

        storage_adapter.create_service(new_service)
        retrieved = storage_adapter.get_service("Azure Container Apps")

        assert retrieved.service == "Azure Container Apps"

    def test_create_service_raises_duplicate_error(
        self, storage_adapter: LocalFileStorageAdapter
    ) -> None:
        """Test that create_service raises DuplicateServiceError for existing name."""
        duplicate_service = ServiceCreate(
            service="Azure Virtual Machines",  # Already exists in sample data
            category="Compute",
            description="Duplicate service.",
        )

        with pytest.raises(DuplicateServiceError, match="Service already exists"):
            storage_adapter.create_service(duplicate_service)

    def test_create_service_in_empty_storage(
        self, empty_storage_adapter: LocalFileStorageAdapter
    ) -> None:
        """Test that create_service works on empty storage."""
        new_service = ServiceCreate(
            service="First Service",
            category="Test",
            description="The first service.",
        )

        result = empty_storage_adapter.create_service(new_service)

        assert result.service == "First Service"
        assert len(empty_storage_adapter.list_services()) == 1

    def test_create_service_preserves_existing_services(
        self, storage_adapter: LocalFileStorageAdapter, sample_services: list[dict]
    ) -> None:
        """Test that create_service doesn't affect existing services."""
        original_count = len(storage_adapter.list_services())

        new_service = ServiceCreate(
            service="New Service",
            category="Test",
            description="A new service.",
        )
        storage_adapter.create_service(new_service)

        assert len(storage_adapter.list_services()) == original_count + 1
