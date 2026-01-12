"""API client for communicating with the backend service.

Provides a typed client with error handling for all CRUD operations
on Azure services.
"""

import logging
from dataclasses import dataclass
from typing import Any

import httpx

from src.config import config

logger = logging.getLogger(__name__)


@dataclass
class ServiceData:
    """Data class representing an Azure service."""

    service: str
    category: str
    description: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ServiceData":
        """Create ServiceData from a dictionary.

        Args:
            data: Dictionary with service, category, description keys.

        Returns:
            ServiceData instance.
        """
        return cls(
            service=data["service"],
            category=data["category"],
            description=data["description"],
        )

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary for API requests.

        Returns:
            Dictionary representation.
        """
        return {
            "service": self.service,
            "category": self.category,
            "description": self.description,
        }


class APIError(Exception):
    """Exception raised for API errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """Initialize API error.

        Args:
            message: Error message.
            status_code: HTTP status code if available.
        """
        super().__init__(message)
        self.status_code = status_code


class APIClient:
    """Client for the Azure Service Catalog API."""

    def __init__(self, base_url: str | None = None, timeout: float = 30.0) -> None:
        """Initialize the API client.

        Args:
            base_url: Override the default API base URL.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url or config.API_BASE_URL
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    def _get_url(self, endpoint: str) -> str:
        """Build full URL for an endpoint.

        Args:
            endpoint: API endpoint (e.g., "services").

        Returns:
            Full URL.
        """
        base = self.base_url.rstrip("/")
        endpoint = endpoint.lstrip("/")
        return f"{base}/api/v1/{endpoint}"

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle API response and raise errors if needed.

        Args:
            response: HTTP response object.

        Returns:
            Parsed JSON response.

        Raises:
            APIError: If response indicates an error.
        """
        try:
            data = response.json()
        except Exception:
            data = {"detail": response.text}

        if response.status_code >= 400:
            error_message = data.get("detail", f"HTTP {response.status_code}")
            logger.error(f"API error: {error_message} (status={response.status_code})")
            raise APIError(error_message, response.status_code)

        return data

    def health_check(self) -> dict[str, Any]:
        """Check API health status.

        Returns:
            Health status response.

        Raises:
            APIError: If health check fails.
        """
        try:
            response = self._client.get(f"{self.base_url}/health")
            return self._handle_response(response)
        except httpx.RequestError as e:
            logger.error(f"Health check failed: {e}")
            raise APIError(f"Cannot connect to API: {e}") from e

    def get_services(
        self,
        category: str | None = None,
        search: str | None = None,
    ) -> list[ServiceData]:
        """Get all services, optionally filtered.

        Args:
            category: Filter by category.
            search: Search in service name or description.

        Returns:
            List of services.

        Raises:
            APIError: If request fails.
        """
        try:
            params = {}
            if category:
                params["category"] = category
            if search:
                params["search"] = search

            response = self._client.get(
                self._get_url("services"),
                params=params,
            )
            data = self._handle_response(response)

            services = data.get("services", [])
            return [ServiceData.from_dict(svc) for svc in services]
        except httpx.RequestError as e:
            logger.error(f"Failed to get services: {e}")
            raise APIError(f"Cannot connect to API: {e}") from e

    def get_service(self, service_name: str) -> ServiceData:
        """Get a single service by name.

        Args:
            service_name: Name of the service.

        Returns:
            Service data.

        Raises:
            APIError: If service not found or request fails.
        """
        try:
            response = self._client.get(
                self._get_url(f"services/{service_name}"),
            )
            data = self._handle_response(response)
            return ServiceData.from_dict(data)
        except httpx.RequestError as e:
            logger.error(f"Failed to get service {service_name}: {e}")
            raise APIError(f"Cannot connect to API: {e}") from e

    def create_service(self, service: ServiceData) -> ServiceData:
        """Create a new service.

        Args:
            service: Service data to create.

        Returns:
            Created service.

        Raises:
            APIError: If creation fails (e.g., duplicate name).
        """
        try:
            response = self._client.post(
                self._get_url("services"),
                json=service.to_dict(),
            )
            data = self._handle_response(response)
            return ServiceData.from_dict(data)
        except httpx.RequestError as e:
            logger.error(f"Failed to create service: {e}")
            raise APIError(f"Cannot connect to API: {e}") from e

    def update_service(
        self,
        service_name: str,
        updates: dict[str, str],
    ) -> ServiceData:
        """Update an existing service.

        Args:
            service_name: Name of the service to update.
            updates: Dictionary of fields to update.

        Returns:
            Updated service.

        Raises:
            APIError: If update fails.
        """
        try:
            response = self._client.put(
                self._get_url(f"services/{service_name}"),
                json=updates,
            )
            data = self._handle_response(response)
            return ServiceData.from_dict(data)
        except httpx.RequestError as e:
            logger.error(f"Failed to update service {service_name}: {e}")
            raise APIError(f"Cannot connect to API: {e}") from e

    def delete_service(self, service_name: str) -> None:
        """Delete a service.

        Args:
            service_name: Name of the service to delete.

        Raises:
            APIError: If deletion fails.
        """
        try:
            response = self._client.delete(
                self._get_url(f"services/{service_name}"),
            )
            if response.status_code >= 400:
                self._handle_response(response)
        except httpx.RequestError as e:
            logger.error(f"Failed to delete service {service_name}: {e}")
            raise APIError(f"Cannot connect to API: {e}") from e

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def simulate_latency(self) -> dict[str, Any]:
        """Trigger latency simulation endpoint.

        Calls the backend simulation endpoint which introduces a random
        delay between 10 and 20 seconds.

        Returns:
            Response with status, delay_seconds, and message.

        Raises:
            APIError: If request fails or times out.
        """
        try:
            response = self._client.post(
                self._get_url("simulate/latency"),
                timeout=30.0,  # Extended timeout for 10-20s delay
            )
            return self._handle_response(response)
        except httpx.TimeoutException as e:
            logger.error(f"Latency simulation timed out: {e}")
            raise APIError("Latency simulation timed out") from e
        except httpx.RequestError as e:
            logger.error(f"Failed to simulate latency: {e}")
            raise APIError(f"Cannot connect to API: {e}") from e

    def simulate_error(self) -> None:
        """Trigger error simulation endpoint.

        Calls the backend simulation endpoint which returns HTTP 500
        with a randomly selected realistic error message.

        Raises:
            APIError: Always raises with simulated error details.
        """
        try:
            response = self._client.post(
                self._get_url("simulate/error"),
            )
            # This will raise APIError due to 500 status
            self._handle_response(response)
        except httpx.RequestError as e:
            logger.error(f"Failed to simulate error: {e}")
            raise APIError(f"Cannot connect to API: {e}") from e

    def __enter__(self) -> "APIClient":
        """Context manager entry."""
        return self

    def __exit__(self, *args) -> None:
        """Context manager exit."""
        self.close()


# Default client instance
api_client = APIClient()
