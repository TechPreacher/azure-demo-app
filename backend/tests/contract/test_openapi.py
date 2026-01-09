"""Contract tests for OpenAPI schema validation.

Validates that the API's OpenAPI schema is well-formed and contains
expected endpoints, models, and response codes.
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


class TestOpenAPISchemaAvailability:
    """Tests for OpenAPI schema endpoint availability."""

    def test_openapi_endpoint_returns_200(self, client: TestClient) -> None:
        """OpenAPI endpoint should return 200 OK."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

    def test_openapi_returns_valid_json(self, client: TestClient) -> None:
        """OpenAPI endpoint should return valid JSON."""
        response = client.get("/openapi.json")
        schema = response.json()
        assert isinstance(schema, dict)

    def test_openapi_contains_info_section(self, client: TestClient) -> None:
        """OpenAPI schema should contain info section."""
        response = client.get("/openapi.json")
        schema = response.json()
        assert "info" in schema
        assert "title" in schema["info"]
        assert "version" in schema["info"]


class TestOpenAPIEndpoints:
    """Tests for expected API endpoints in OpenAPI schema."""

    def test_health_endpoint_documented(self, client: TestClient) -> None:
        """Health endpoint should be documented."""
        response = client.get("/openapi.json")
        schema = response.json()
        assert "/health" in schema["paths"]
        assert "get" in schema["paths"]["/health"]

    def test_services_list_endpoint_documented(self, client: TestClient) -> None:
        """GET /api/v1/services endpoint should be documented."""
        response = client.get("/openapi.json")
        schema = response.json()
        assert "/api/v1/services" in schema["paths"]
        assert "get" in schema["paths"]["/api/v1/services"]

    def test_services_create_endpoint_documented(self, client: TestClient) -> None:
        """POST /api/v1/services endpoint should be documented."""
        response = client.get("/openapi.json")
        schema = response.json()
        assert "/api/v1/services" in schema["paths"]
        assert "post" in schema["paths"]["/api/v1/services"]

    def test_service_get_by_name_endpoint_documented(self, client: TestClient) -> None:
        """GET /api/v1/services/{name} endpoint should be documented."""
        response = client.get("/openapi.json")
        schema = response.json()
        assert "/api/v1/services/{service_name}" in schema["paths"]
        assert "get" in schema["paths"]["/api/v1/services/{service_name}"]

    def test_service_update_endpoint_documented(self, client: TestClient) -> None:
        """PUT /api/v1/services/{name} endpoint should be documented."""
        response = client.get("/openapi.json")
        schema = response.json()
        assert "/api/v1/services/{service_name}" in schema["paths"]
        assert "put" in schema["paths"]["/api/v1/services/{service_name}"]

    def test_service_delete_endpoint_documented(self, client: TestClient) -> None:
        """DELETE /api/v1/services/{name} endpoint should be documented."""
        response = client.get("/openapi.json")
        schema = response.json()
        assert "/api/v1/services/{service_name}" in schema["paths"]
        assert "delete" in schema["paths"]["/api/v1/services/{service_name}"]


class TestOpenAPIResponseCodes:
    """Tests for expected response codes in OpenAPI schema."""

    def test_services_list_returns_200(self, client: TestClient) -> None:
        """GET /api/v1/services should document 200 response."""
        response = client.get("/openapi.json")
        schema = response.json()
        responses = schema["paths"]["/api/v1/services"]["get"]["responses"]
        assert "200" in responses

    def test_services_create_returns_201(self, client: TestClient) -> None:
        """POST /api/v1/services should document 201 response."""
        response = client.get("/openapi.json")
        schema = response.json()
        responses = schema["paths"]["/api/v1/services"]["post"]["responses"]
        assert "201" in responses

    def test_service_get_returns_200_and_404(self, client: TestClient) -> None:
        """GET /api/v1/services/{name} should document 200 and 404 responses."""
        response = client.get("/openapi.json")
        schema = response.json()
        responses = schema["paths"]["/api/v1/services/{service_name}"]["get"]["responses"]
        assert "200" in responses
        assert "404" in responses

    def test_service_update_returns_200_and_404(self, client: TestClient) -> None:
        """PUT /api/v1/services/{name} should document 200 and 404 responses."""
        response = client.get("/openapi.json")
        schema = response.json()
        responses = schema["paths"]["/api/v1/services/{service_name}"]["put"]["responses"]
        assert "200" in responses
        assert "404" in responses

    def test_service_delete_returns_204_and_404(self, client: TestClient) -> None:
        """DELETE /api/v1/services/{name} should document 204 and 404 responses."""
        response = client.get("/openapi.json")
        schema = response.json()
        responses = schema["paths"]["/api/v1/services/{service_name}"]["delete"]["responses"]
        assert "204" in responses
        assert "404" in responses


class TestOpenAPIModels:
    """Tests for expected models in OpenAPI schema."""

    def test_service_model_documented(self, client: TestClient) -> None:
        """Service model should be documented in components."""
        response = client.get("/openapi.json")
        schema = response.json()
        assert "components" in schema
        assert "schemas" in schema["components"]
        assert "Service" in schema["components"]["schemas"]

    def test_service_model_has_required_fields(self, client: TestClient) -> None:
        """Service model should have service, category, description fields."""
        response = client.get("/openapi.json")
        schema = response.json()
        service_schema = schema["components"]["schemas"]["Service"]
        properties = service_schema.get("properties", {})
        assert "service" in properties  # service name field
        assert "category" in properties
        assert "description" in properties

    def test_service_create_model_documented(self, client: TestClient) -> None:
        """ServiceCreate model should be documented."""
        response = client.get("/openapi.json")
        schema = response.json()
        assert "ServiceCreate" in schema["components"]["schemas"]

    def test_service_update_model_documented(self, client: TestClient) -> None:
        """ServiceUpdate model should be documented."""
        response = client.get("/openapi.json")
        schema = response.json()
        assert "ServiceUpdate" in schema["components"]["schemas"]


class TestOpenAPIMetadata:
    """Tests for OpenAPI metadata and configuration."""

    def test_api_title_is_correct(self, client: TestClient) -> None:
        """API title should be Azure Service Catalog API."""
        response = client.get("/openapi.json")
        schema = response.json()
        assert schema["info"]["title"] == "Azure Service Catalog API"

    def test_api_version_is_set(self, client: TestClient) -> None:
        """API version should be set."""
        response = client.get("/openapi.json")
        schema = response.json()
        assert schema["info"]["version"] == "1.0.0"

    def test_openapi_version_is_3(self, client: TestClient) -> None:
        """OpenAPI version should be 3.x."""
        response = client.get("/openapi.json")
        schema = response.json()
        assert schema["openapi"].startswith("3.")
