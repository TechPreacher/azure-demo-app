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


class TestCreateServiceEndpoint:
    """Integration tests for POST /api/v1/services endpoint."""

    def test_create_service_returns_201(self, api_client: TestClient) -> None:
        """Test that endpoint returns 201 for successful creation."""
        new_service = {
            "service": "Azure Container Apps",
            "category": "Containers",
            "description": "Fully managed serverless container service.",
        }

        response = api_client.post("/api/v1/services", json=new_service)

        assert response.status_code == 201

    def test_create_service_returns_created_service(
        self, api_client: TestClient
    ) -> None:
        """Test that endpoint returns the created service data."""
        new_service = {
            "service": "Azure Functions",
            "category": "Serverless",
            "description": "Event-driven serverless compute platform.",
        }

        response = api_client.post("/api/v1/services", json=new_service)
        data = response.json()

        assert data["service"] == "Azure Functions"
        assert data["category"] == "Serverless"
        assert data["description"] == "Event-driven serverless compute platform."

    def test_create_service_persists(self, api_client: TestClient) -> None:
        """Test that created service can be retrieved."""
        new_service = {
            "service": "Azure Logic Apps",
            "category": "Integration",
            "description": "Cloud-based workflow automation.",
        }

        api_client.post("/api/v1/services", json=new_service)
        get_response = api_client.get("/api/v1/services/Azure Logic Apps")

        assert get_response.status_code == 200
        assert get_response.json()["service"] == "Azure Logic Apps"

    def test_create_service_returns_409_for_duplicate(
        self, api_client: TestClient
    ) -> None:
        """Test that endpoint returns 409 for duplicate service name."""
        duplicate_service = {
            "service": "Azure Virtual Machines",  # Already exists
            "category": "Compute",
            "description": "Duplicate service.",
        }

        response = api_client.post("/api/v1/services", json=duplicate_service)

        assert response.status_code == 409

    def test_create_service_409_includes_detail(self, api_client: TestClient) -> None:
        """Test that 409 response includes error detail."""
        duplicate_service = {
            "service": "Azure Virtual Machines",
            "category": "Compute",
            "description": "Duplicate.",
        }

        response = api_client.post("/api/v1/services", json=duplicate_service)
        data = response.json()

        assert "detail" in data
        assert "already exists" in data["detail"].lower()

    def test_create_service_returns_422_for_invalid_data(
        self, api_client: TestClient
    ) -> None:
        """Test that endpoint returns 422 for invalid request data."""
        invalid_service = {
            "service": "Missing Fields",
            # Missing category and description
        }

        response = api_client.post("/api/v1/services", json=invalid_service)

        assert response.status_code == 422

    def test_create_service_increases_total_count(
        self, api_client: TestClient, test_services: list[dict]
    ) -> None:
        """Test that creating a service increases the total count."""
        initial_response = api_client.get("/api/v1/services")
        initial_count = initial_response.json()["total"]

        new_service = {
            "service": "New Test Service",
            "category": "Test",
            "description": "A test service.",
        }
        api_client.post("/api/v1/services", json=new_service)

        final_response = api_client.get("/api/v1/services")
        final_count = final_response.json()["total"]

        assert final_count == initial_count + 1


class TestUpdateServiceEndpoint:
    """Integration tests for PUT /api/v1/services/{service_name} endpoint."""

    def test_update_service_returns_200(self, api_client: TestClient) -> None:
        """Test that endpoint returns 200 for successful update."""
        update_data = {"description": "Updated VM description."}

        response = api_client.put(
            "/api/v1/services/Azure Virtual Machines", json=update_data
        )

        assert response.status_code == 200

    def test_update_service_returns_updated_service(
        self, api_client: TestClient
    ) -> None:
        """Test that endpoint returns the updated service data."""
        update_data = {"description": "Newly updated description."}

        response = api_client.put(
            "/api/v1/services/Azure Virtual Machines", json=update_data
        )
        data = response.json()

        assert data["service"] == "Azure Virtual Machines"
        assert data["description"] == "Newly updated description."
        assert data["category"] == "Compute"

    def test_update_service_changes_category(self, api_client: TestClient) -> None:
        """Test that endpoint can update category field."""
        update_data = {"category": "Infrastructure"}

        response = api_client.put(
            "/api/v1/services/Azure Virtual Machines", json=update_data
        )
        data = response.json()

        assert data["category"] == "Infrastructure"

    def test_update_service_changes_name(self, api_client: TestClient) -> None:
        """Test that endpoint can rename a service."""
        update_data = {"service": "Azure VMs"}

        response = api_client.put(
            "/api/v1/services/Azure Virtual Machines", json=update_data
        )
        data = response.json()

        assert response.status_code == 200
        assert data["service"] == "Azure VMs"

        # Verify new name can be retrieved
        get_response = api_client.get("/api/v1/services/Azure VMs")
        assert get_response.status_code == 200

        # Verify old name no longer exists
        old_response = api_client.get("/api/v1/services/Azure Virtual Machines")
        assert old_response.status_code == 404

    def test_update_service_changes_multiple_fields(
        self, api_client: TestClient
    ) -> None:
        """Test that endpoint can update multiple fields at once."""
        update_data = {
            "service": "Azure VMs",
            "category": "Infrastructure",
            "description": "Virtual machines for all workloads.",
        }

        response = api_client.put(
            "/api/v1/services/Azure Virtual Machines", json=update_data
        )
        data = response.json()

        assert data["service"] == "Azure VMs"
        assert data["category"] == "Infrastructure"
        assert data["description"] == "Virtual machines for all workloads."

    def test_update_service_persists(self, api_client: TestClient) -> None:
        """Test that updated service changes persist."""
        update_data = {"description": "Persisted update."}

        api_client.put("/api/v1/services/Azure Virtual Machines", json=update_data)

        get_response = api_client.get("/api/v1/services/Azure Virtual Machines")
        data = get_response.json()

        assert data["description"] == "Persisted update."

    def test_update_service_returns_404_for_missing(
        self, api_client: TestClient
    ) -> None:
        """Test that endpoint returns 404 for nonexistent service."""
        update_data = {"description": "Update attempt."}

        response = api_client.put("/api/v1/services/Nonexistent Service", json=update_data)

        assert response.status_code == 404

    def test_update_service_404_includes_detail(self, api_client: TestClient) -> None:
        """Test that 404 response includes error detail."""
        update_data = {"description": "Update."}

        response = api_client.put("/api/v1/services/Nonexistent Service", json=update_data)
        data = response.json()

        assert "detail" in data

    def test_update_service_returns_409_for_name_conflict(
        self, api_client: TestClient
    ) -> None:
        """Test that endpoint returns 409 when renaming to existing name."""
        update_data = {"service": "Azure SQL Database"}  # Already exists

        response = api_client.put(
            "/api/v1/services/Azure Virtual Machines", json=update_data
        )

        assert response.status_code == 409

    def test_update_service_409_includes_detail(self, api_client: TestClient) -> None:
        """Test that 409 response includes error detail."""
        update_data = {"service": "Azure SQL Database"}

        response = api_client.put(
            "/api/v1/services/Azure Virtual Machines", json=update_data
        )
        data = response.json()

        assert "detail" in data
        assert "already exists" in data["detail"].lower()

    def test_update_service_preserves_total_count(
        self, api_client: TestClient, test_services: list[dict]
    ) -> None:
        """Test that updating doesn't change total service count."""
        initial_response = api_client.get("/api/v1/services")
        initial_count = initial_response.json()["total"]

        update_data = {"description": "Updated."}
        api_client.put("/api/v1/services/Azure Virtual Machines", json=update_data)

        final_response = api_client.get("/api/v1/services")
        final_count = final_response.json()["total"]

        assert final_count == initial_count


class TestDeleteServiceEndpoint:
    """Integration tests for DELETE /api/v1/services/{service_name} endpoint."""

    def test_delete_service_returns_204(self, api_client: TestClient) -> None:
        """Test that endpoint returns 204 for successful deletion."""
        response = api_client.delete("/api/v1/services/Azure Virtual Machines")

        assert response.status_code == 204

    def test_delete_service_removes_service(self, api_client: TestClient) -> None:
        """Test that deleted service can no longer be retrieved."""
        api_client.delete("/api/v1/services/Azure Virtual Machines")

        get_response = api_client.get("/api/v1/services/Azure Virtual Machines")
        assert get_response.status_code == 404

    def test_delete_service_decreases_count(
        self, api_client: TestClient, test_services: list[dict]
    ) -> None:
        """Test that deleting a service decreases the total count."""
        initial_response = api_client.get("/api/v1/services")
        initial_count = initial_response.json()["total"]

        api_client.delete("/api/v1/services/Azure Virtual Machines")

        final_response = api_client.get("/api/v1/services")
        final_count = final_response.json()["total"]

        assert final_count == initial_count - 1

    def test_delete_service_returns_404_for_missing(
        self, api_client: TestClient
    ) -> None:
        """Test that endpoint returns 404 for nonexistent service."""
        response = api_client.delete("/api/v1/services/Nonexistent Service")

        assert response.status_code == 404

    def test_delete_service_404_includes_detail(self, api_client: TestClient) -> None:
        """Test that 404 response includes error detail."""
        response = api_client.delete("/api/v1/services/Nonexistent Service")
        data = response.json()

        assert "detail" in data

    def test_delete_service_preserves_other_services(
        self, api_client: TestClient
    ) -> None:
        """Test that deleting doesn't affect other services."""
        api_client.delete("/api/v1/services/Azure Virtual Machines")

        # Other services should still exist
        sql_response = api_client.get("/api/v1/services/Azure SQL Database")
        assert sql_response.status_code == 200

        app_response = api_client.get("/api/v1/services/Azure App Service")
        assert app_response.status_code == 200

    def test_delete_service_is_idempotent_fails_second_time(
        self, api_client: TestClient
    ) -> None:
        """Test that deleting same service twice fails the second time."""
        # First delete succeeds
        response1 = api_client.delete("/api/v1/services/Azure Virtual Machines")
        assert response1.status_code == 204

        # Second delete fails
        response2 = api_client.delete("/api/v1/services/Azure Virtual Machines")
        assert response2.status_code == 404
