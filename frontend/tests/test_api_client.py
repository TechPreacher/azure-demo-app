"""Tests for the frontend API client.

Tests the APIClient class functionality with mocked responses.
"""

import pytest
from unittest.mock import MagicMock, patch

import httpx

from src.api_client import APIClient, APIError, ServiceData


class TestAPIClientGetServices:
    """Tests for APIClient.get_services() method."""

    def test_get_services_returns_list_of_services(
        self, sample_services: list[ServiceData]
    ) -> None:
        """Test that get_services returns a list of ServiceData objects."""
        mock_response_data = {
            "services": [svc.to_dict() for svc in sample_services],
            "total": len(sample_services),
        }

        with patch.object(httpx.Client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response

            client = APIClient(base_url="http://test-api:8000")
            result = client.get_services()

            assert len(result) == len(sample_services)
            assert all(isinstance(svc, ServiceData) for svc in result)

    def test_get_services_returns_empty_list_when_no_services(self) -> None:
        """Test that get_services returns empty list when API returns no services."""
        mock_response_data = {"services": [], "total": 0}

        with patch.object(httpx.Client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response

            client = APIClient(base_url="http://test-api:8000")
            result = client.get_services()

            assert result == []

    def test_get_services_passes_category_filter(self) -> None:
        """Test that category filter is passed as query parameter."""
        mock_response_data = {"services": [], "total": 0}

        with patch.object(httpx.Client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response

            client = APIClient(base_url="http://test-api:8000")
            client.get_services(category="Compute")

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args.kwargs["params"]["category"] == "Compute"

    def test_get_services_passes_search_filter(self) -> None:
        """Test that search filter is passed as query parameter."""
        mock_response_data = {"services": [], "total": 0}

        with patch.object(httpx.Client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response

            client = APIClient(base_url="http://test-api:8000")
            client.get_services(search="virtual")

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args.kwargs["params"]["search"] == "virtual"

    def test_get_services_passes_both_filters(self) -> None:
        """Test that both filters are passed as query parameters."""
        mock_response_data = {"services": [], "total": 0}

        with patch.object(httpx.Client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response

            client = APIClient(base_url="http://test-api:8000")
            client.get_services(category="Databases", search="sql")

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args.kwargs["params"]["category"] == "Databases"
            assert call_args.kwargs["params"]["search"] == "sql"

    def test_get_services_raises_api_error_on_server_error(self) -> None:
        """Test that get_services raises APIError on server error."""
        with patch.object(httpx.Client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.json.return_value = {"detail": "Internal Server Error"}
            mock_get.return_value = mock_response

            client = APIClient(base_url="http://test-api:8000")

            with pytest.raises(APIError) as exc_info:
                client.get_services()

            assert exc_info.value.status_code == 500

    def test_get_services_raises_api_error_on_connection_error(self) -> None:
        """Test that get_services raises APIError on connection error."""
        with patch.object(httpx.Client, "get") as mock_get:
            mock_get.side_effect = httpx.RequestError("Connection failed")

            client = APIClient(base_url="http://test-api:8000")

            with pytest.raises(APIError, match="Cannot connect to API"):
                client.get_services()


class TestAPIClientGetService:
    """Tests for APIClient.get_service() method."""

    def test_get_service_returns_service_data(
        self, sample_service: ServiceData
    ) -> None:
        """Test that get_service returns ServiceData object."""
        with patch.object(httpx.Client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_service.to_dict()
            mock_get.return_value = mock_response

            client = APIClient(base_url="http://test-api:8000")
            result = client.get_service("Azure Virtual Machines")

            assert isinstance(result, ServiceData)
            assert result.service == sample_service.service
            assert result.category == sample_service.category

    def test_get_service_raises_api_error_on_404(self) -> None:
        """Test that get_service raises APIError on 404."""
        with patch.object(httpx.Client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.json.return_value = {"detail": "Service not found"}
            mock_get.return_value = mock_response

            client = APIClient(base_url="http://test-api:8000")

            with pytest.raises(APIError) as exc_info:
                client.get_service("Nonexistent Service")

            assert exc_info.value.status_code == 404

    def test_get_service_calls_correct_endpoint(self) -> None:
        """Test that get_service calls the correct URL."""
        with patch.object(httpx.Client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "service": "Test",
                "category": "Test",
                "description": "Test",
            }
            mock_get.return_value = mock_response

            client = APIClient(base_url="http://test-api:8000")
            client.get_service("Azure VM")

            mock_get.assert_called_once()
            call_url = mock_get.call_args[0][0]
            assert "services/Azure VM" in call_url


class TestServiceData:
    """Tests for ServiceData dataclass."""

    def test_from_dict_creates_instance(self) -> None:
        """Test that from_dict creates ServiceData from dict."""
        data = {
            "service": "Test Service",
            "category": "Test Category",
            "description": "Test Description",
        }

        result = ServiceData.from_dict(data)

        assert result.service == "Test Service"
        assert result.category == "Test Category"
        assert result.description == "Test Description"

    def test_to_dict_returns_dict(self, sample_service: ServiceData) -> None:
        """Test that to_dict returns correct dict."""
        result = sample_service.to_dict()

        assert result["service"] == sample_service.service
        assert result["category"] == sample_service.category
        assert result["description"] == sample_service.description


class TestAPIClientCreateService:
    """Tests for APIClient.create_service() method."""

    def test_create_service_returns_service_data(
        self, sample_service: ServiceData
    ) -> None:
        """Test that create_service returns ServiceData object."""
        with patch.object(httpx.Client, "post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = sample_service.to_dict()
            mock_post.return_value = mock_response

            client = APIClient(base_url="http://test-api:8000")
            result = client.create_service(sample_service)

            assert isinstance(result, ServiceData)
            assert result.service == sample_service.service
            assert result.category == sample_service.category

    def test_create_service_sends_correct_data(
        self, sample_service: ServiceData
    ) -> None:
        """Test that create_service sends correct JSON payload."""
        with patch.object(httpx.Client, "post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = sample_service.to_dict()
            mock_post.return_value = mock_response

            client = APIClient(base_url="http://test-api:8000")
            client.create_service(sample_service)

            mock_post.assert_called_once()
            call_kwargs = mock_post.call_args.kwargs
            assert call_kwargs["json"] == sample_service.to_dict()

    def test_create_service_raises_api_error_on_409(self) -> None:
        """Test that create_service raises APIError on duplicate (409)."""
        with patch.object(httpx.Client, "post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 409
            mock_response.json.return_value = {"detail": "Service already exists"}
            mock_post.return_value = mock_response

            client = APIClient(base_url="http://test-api:8000")
            service = ServiceData(
                service="Duplicate",
                category="Test",
                description="Test",
            )

            with pytest.raises(APIError) as exc_info:
                client.create_service(service)

            assert exc_info.value.status_code == 409

    def test_create_service_raises_api_error_on_validation_error(self) -> None:
        """Test that create_service raises APIError on validation error (422)."""
        with patch.object(httpx.Client, "post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 422
            mock_response.json.return_value = {"detail": "Validation error"}
            mock_post.return_value = mock_response

            client = APIClient(base_url="http://test-api:8000")
            service = ServiceData(
                service="Invalid",
                category="",
                description="",
            )

            with pytest.raises(APIError) as exc_info:
                client.create_service(service)

            assert exc_info.value.status_code == 422

    def test_create_service_raises_api_error_on_connection_error(self) -> None:
        """Test that create_service raises APIError on connection error."""
        with patch.object(httpx.Client, "post") as mock_post:
            mock_post.side_effect = httpx.RequestError("Connection failed")

            client = APIClient(base_url="http://test-api:8000")
            service = ServiceData(
                service="Test",
                category="Test",
                description="Test",
            )

            with pytest.raises(APIError, match="Cannot connect to API"):
                client.create_service(service)
