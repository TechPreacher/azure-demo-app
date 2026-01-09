"""Integration tests for API endpoints.

Tests the FastAPI routes with a test client.
"""

import json
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from src.config import Settings, get_settings
from src.main import create_app
from src.services.storage import LocalFileStorageAdapter


@pytest.fixture
def test_services() -> list[dict]:
    """Sample services for integration tests."""
    return [
        {
            "service": "Azure Virtual Machines",
            "category": "Compute",
            "description": "On-demand, scalable virtual machines.",
        },
        {
            "service": "Azure App Service",
            "category": "App Platform",
            "description": "Fully managed platform for web apps.",
        },
        {
            "service": "Azure SQL Database",
            "category": "Databases",
            "description": "Managed SQL database service.",
        },
        {
            "service": "Azure Cosmos DB",
            "category": "Databases",
            "description": "Globally distributed NoSQL database.",
        },
    ]


@pytest.fixture
def temp_data_file(test_services: list[dict]) -> Generator[Path, None, None]:
    """Create a temporary services.json file."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        json.dump({"services": test_services}, f)
        temp_path = Path(f.name)

    yield temp_path

    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def test_settings(temp_data_file: Path) -> Settings:
    """Create test settings pointing to temp file."""
    return Settings(
        storage_type="local",
        local_data_path=str(temp_data_file),
        debug=True,
    )


@pytest.fixture
def api_client(test_settings: Settings) -> Generator[TestClient, None, None]:
    """Create a test client with test settings and storage."""
    app = create_app()

    # Override the settings and storage dependencies
    def override_get_settings() -> Settings:
        return test_settings

    def override_get_storage() -> LocalFileStorageAdapter:
        return LocalFileStorageAdapter(test_settings.local_data_path)

    from src.api.dependencies import get_storage

    app.dependency_overrides[get_settings] = override_get_settings
    app.dependency_overrides[get_storage] = override_get_storage

    with TestClient(app) as client:
        yield client


class TestGetServicesEndpoint:
    """Integration tests for GET /api/v1/services endpoint."""

    def test_get_services_returns_200(self, api_client: TestClient) -> None:
        """Test that endpoint returns 200 status."""
        response = api_client.get("/api/v1/services")

        assert response.status_code == 200

    def test_get_services_returns_service_list(
        self, api_client: TestClient, test_services: list[dict]
    ) -> None:
        """Test that endpoint returns all services."""
        response = api_client.get("/api/v1/services")
        data = response.json()

        assert "services" in data
        assert "total" in data
        assert data["total"] == len(test_services)
        assert len(data["services"]) == len(test_services)

    def test_get_services_returns_correct_structure(
        self, api_client: TestClient
    ) -> None:
        """Test that services have correct fields."""
        response = api_client.get("/api/v1/services")
        data = response.json()

        assert len(data["services"]) > 0
        service = data["services"][0]

        assert "service" in service
        assert "category" in service
        assert "description" in service

    def test_get_services_filters_by_category(self, api_client: TestClient) -> None:
        """Test category filter query parameter."""
        response = api_client.get("/api/v1/services?category=Databases")
        data = response.json()

        assert response.status_code == 200
        assert data["total"] == 2
        assert all(svc["category"] == "Databases" for svc in data["services"])

    def test_get_services_filters_by_search(self, api_client: TestClient) -> None:
        """Test search filter query parameter."""
        response = api_client.get("/api/v1/services?search=virtual")
        data = response.json()

        assert response.status_code == 200
        assert data["total"] >= 1
        assert any(
            "virtual" in svc["service"].lower() or "virtual" in svc["description"].lower()
            for svc in data["services"]
        )

    def test_get_services_combines_filters(self, api_client: TestClient) -> None:
        """Test combining category and search filters."""
        response = api_client.get("/api/v1/services?category=Databases&search=managed")
        data = response.json()

        assert response.status_code == 200
        # Both Azure SQL Database and Azure Cosmos DB have "Managed" in description
        assert data["total"] >= 1
        assert all(svc["category"] == "Databases" for svc in data["services"])

    def test_get_services_empty_result(self, api_client: TestClient) -> None:
        """Test endpoint returns empty list for no matches."""
        response = api_client.get("/api/v1/services?category=NonexistentCategory")
        data = response.json()

        assert response.status_code == 200
        assert data["total"] == 0
        assert data["services"] == []


class TestGetServiceByNameEndpoint:
    """Integration tests for GET /api/v1/services/{service_name} endpoint."""

    def test_get_service_returns_200(self, api_client: TestClient) -> None:
        """Test that endpoint returns 200 for existing service."""
        response = api_client.get("/api/v1/services/Azure Virtual Machines")

        assert response.status_code == 200

    def test_get_service_returns_correct_service(self, api_client: TestClient) -> None:
        """Test that endpoint returns the correct service data."""
        response = api_client.get("/api/v1/services/Azure Virtual Machines")
        data = response.json()

        assert data["service"] == "Azure Virtual Machines"
        assert data["category"] == "Compute"
        assert "description" in data

    def test_get_service_returns_404_for_missing(self, api_client: TestClient) -> None:
        """Test that endpoint returns 404 for nonexistent service."""
        response = api_client.get("/api/v1/services/Nonexistent Service")

        assert response.status_code == 404

    def test_get_service_404_includes_detail(self, api_client: TestClient) -> None:
        """Test that 404 response includes error detail."""
        response = api_client.get("/api/v1/services/Nonexistent Service")
        data = response.json()

        assert "detail" in data


class TestHealthEndpoint:
    """Integration tests for health check endpoint."""

    def test_health_returns_200(self, api_client: TestClient) -> None:
        """Test that health endpoint returns 200."""
        response = api_client.get("/health")

        assert response.status_code == 200

    def test_health_returns_healthy_status(self, api_client: TestClient) -> None:
        """Test that health endpoint returns healthy status."""
        response = api_client.get("/health")
        data = response.json()

        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
