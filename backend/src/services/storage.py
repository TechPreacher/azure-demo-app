"""Storage adapters for Azure services data.

Provides abstract interface and concrete implementations for:
- LocalFileStorageAdapter: Development - reads/writes local JSON file
- AzureBlobStorageAdapter: Production - reads/writes Azure Blob Storage

Instrumented with OpenTelemetry spans for observability.
"""

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from opentelemetry import trace

from src.models.service import Service, ServiceCreate, ServiceUpdate

if TYPE_CHECKING:
    from src.config import Settings

logger = logging.getLogger(__name__)

# Create tracer for storage operations
tracer = trace.get_tracer(__name__)


class StorageError(Exception):
    """Base exception for storage operations."""

    pass


class ServiceNotFoundError(StorageError):
    """Raised when a service is not found."""

    pass


class DuplicateServiceError(StorageError):
    """Raised when attempting to create a service that already exists."""

    pass


class StorageAdapter(ABC):
    """Abstract base class for storage adapters."""

    @abstractmethod
    def list_services(
        self,
        category: str | None = None,
        search: str | None = None,
    ) -> list[Service]:
        """List all services, optionally filtered.

        Args:
            category: Filter by category (case-insensitive).
            search: Search in service name or description (case-insensitive).

        Returns:
            List of services matching the filters.
        """
        pass

    @abstractmethod
    def get_service(self, service_name: str) -> Service:
        """Get a single service by name.

        Args:
            service_name: Exact name of the service.

        Returns:
            The service if found.

        Raises:
            ServiceNotFoundError: If service doesn't exist.
        """
        pass

    @abstractmethod
    def create_service(self, service: ServiceCreate) -> Service:
        """Create a new service.

        Args:
            service: Service data to create.

        Returns:
            The created service.

        Raises:
            DuplicateServiceError: If service name already exists.
        """
        pass

    @abstractmethod
    def update_service(self, service_name: str, update: ServiceUpdate) -> Service:
        """Update an existing service.

        Args:
            service_name: Name of the service to update.
            update: Fields to update (partial update supported).

        Returns:
            The updated service.

        Raises:
            ServiceNotFoundError: If service doesn't exist.
            DuplicateServiceError: If new name conflicts with existing service.
        """
        pass

    @abstractmethod
    def delete_service(self, service_name: str) -> None:
        """Delete a service.

        Args:
            service_name: Name of the service to delete.

        Raises:
            ServiceNotFoundError: If service doesn't exist.
        """
        pass


class LocalFileStorageAdapter(StorageAdapter):
    """Storage adapter that reads/writes to a local JSON file.

    Used for local development without Azure dependencies.
    """

    def __init__(self, file_path: str) -> None:
        """Initialize the local file storage adapter.

        Args:
            file_path: Path to the services.json file.
        """
        self.file_path = Path(file_path)
        logger.info(f"LocalFileStorageAdapter initialized with path: {self.file_path}")

    def _read_data(self) -> list[dict]:
        """Read services from the JSON file.

        Returns:
            List of service dictionaries.

        Raises:
            StorageError: If file cannot be read or parsed.
        """
        if not self.file_path.exists():
            logger.warning(f"File not found: {self.file_path}, returning empty list")
            return []

        try:
            with open(self.file_path, encoding="utf-8") as f:
                data = json.load(f)
                # Handle both {"services": [...]} and [...] formats
                if isinstance(data, dict) and "services" in data:
                    return data["services"]
                if isinstance(data, list):
                    return data
                raise StorageError(f"Unexpected JSON structure in {self.file_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from {self.file_path}: {e}")
            raise StorageError(f"Invalid JSON in {self.file_path}") from e
        except OSError as e:
            logger.error(f"Failed to read {self.file_path}: {e}")
            raise StorageError(f"Cannot read {self.file_path}") from e

    def _write_data(self, services: list[dict]) -> None:
        """Write services to the JSON file.

        Args:
            services: List of service dictionaries to write.

        Raises:
            StorageError: If file cannot be written.
        """
        try:
            # Ensure directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({"services": services}, f, indent=4, ensure_ascii=False)
            logger.debug(f"Wrote {len(services)} services to {self.file_path}")
        except OSError as e:
            logger.error(f"Failed to write {self.file_path}: {e}")
            raise StorageError(f"Cannot write {self.file_path}") from e

    def list_services(
        self,
        category: str | None = None,
        search: str | None = None,
    ) -> list[Service]:
        """List all services, optionally filtered."""
        with tracer.start_as_current_span("storage.list_services") as span:
            span.set_attribute("storage.type", "local")
            span.set_attribute("storage.file_path", str(self.file_path))
            if category:
                span.set_attribute("filter.category", category)
            if search:
                span.set_attribute("filter.search", search)

            try:
                services = self._read_data()
                result = []

                for svc in services:
                    # Apply category filter
                    if category and svc.get("category", "").lower() != category.lower():
                        continue

                    # Apply search filter
                    if search:
                        search_lower = search.lower()
                        name_match = search_lower in svc.get("service", "").lower()
                        desc_match = search_lower in svc.get("description", "").lower()
                        if not (name_match or desc_match):
                            continue

                    result.append(Service(**svc))

                span.set_attribute("result.count", len(result))
                return result
            except Exception as e:
                span.set_status(trace.StatusCode.ERROR, str(e))
                span.record_exception(e)
                raise

    def get_service(self, service_name: str) -> Service:
        """Get a single service by name."""
        with tracer.start_as_current_span("storage.get_service") as span:
            span.set_attribute("storage.type", "local")
            span.set_attribute("service.name", service_name)

            try:
                services = self._read_data()

                for svc in services:
                    if svc.get("service") == service_name:
                        span.set_attribute("result.found", True)
                        return Service(**svc)

                span.set_attribute("result.found", False)
                raise ServiceNotFoundError(f"Service not found: {service_name}")
            except ServiceNotFoundError:
                raise
            except Exception as e:
                span.set_status(trace.StatusCode.ERROR, str(e))
                span.record_exception(e)
                raise

    def create_service(self, service: ServiceCreate) -> Service:
        """Create a new service."""
        with tracer.start_as_current_span("storage.create_service") as span:
            span.set_attribute("storage.type", "local")
            span.set_attribute("service.name", service.service)

            try:
                services = self._read_data()

                # Check for duplicate
                for svc in services:
                    if svc.get("service") == service.service:
                        span.set_attribute("result.duplicate", True)
                        raise DuplicateServiceError(f"Service already exists: {service.service}")

                # Add new service
                new_service = service.model_dump()
                services.append(new_service)
                self._write_data(services)

                span.set_attribute("result.created", True)
                logger.info(f"Created service: {service.service}")
                return Service(**new_service)
            except DuplicateServiceError:
                raise
            except Exception as e:
                span.set_status(trace.StatusCode.ERROR, str(e))
                span.record_exception(e)
                raise

    def update_service(self, service_name: str, update: ServiceUpdate) -> Service:
        """Update an existing service."""
        with tracer.start_as_current_span("storage.update_service") as span:
            span.set_attribute("storage.type", "local")
            span.set_attribute("service.name", service_name)
            if update.service:
                span.set_attribute("service.new_name", update.service)

            try:
                services = self._read_data()
                found_index = None

                for i, svc in enumerate(services):
                    if svc.get("service") == service_name:
                        found_index = i
                        break

                if found_index is None:
                    span.set_attribute("result.found", False)
                    raise ServiceNotFoundError(f"Service not found: {service_name}")

                # Check if new name conflicts with existing service
                if update.service and update.service != service_name:
                    for svc in services:
                        if svc.get("service") == update.service:
                            span.set_attribute("result.duplicate", True)
                            raise DuplicateServiceError(f"Service already exists: {update.service}")

                # Apply updates (only non-None fields)
                update_data = update.model_dump(exclude_none=True)
                services[found_index].update(update_data)
                self._write_data(services)

                span.set_attribute("result.updated", True)
                logger.info(f"Updated service: {service_name}")
                return Service(**services[found_index])
            except (ServiceNotFoundError, DuplicateServiceError):
                raise
            except Exception as e:
                span.set_status(trace.StatusCode.ERROR, str(e))
                span.record_exception(e)
                raise

    def delete_service(self, service_name: str) -> None:
        """Delete a service."""
        with tracer.start_as_current_span("storage.delete_service") as span:
            span.set_attribute("storage.type", "local")
            span.set_attribute("service.name", service_name)

            try:
                services = self._read_data()
                original_count = len(services)

                services = [svc for svc in services if svc.get("service") != service_name]

                if len(services) == original_count:
                    span.set_attribute("result.found", False)
                    raise ServiceNotFoundError(f"Service not found: {service_name}")

                self._write_data(services)
                span.set_attribute("result.deleted", True)
                logger.info(f"Deleted service: {service_name}")
            except ServiceNotFoundError:
                raise
            except Exception as e:
                span.set_status(trace.StatusCode.ERROR, str(e))
                span.record_exception(e)
                raise


class AzureBlobStorageAdapter(StorageAdapter):
    """Storage adapter that reads/writes to Azure Blob Storage.

    Used in production Azure environment. Supports both managed identity
    and connection string authentication.
    """

    def __init__(
        self,
        container_name: str,
        blob_name: str = "services.json",
        account_name: str | None = None,
        connection_string: str | None = None,
        use_managed_identity: bool = False,
    ) -> None:
        """Initialize the Azure Blob storage adapter.

        Args:
            container_name: Name of the blob container.
            blob_name: Name of the JSON blob file.
            account_name: Storage account name (required for managed identity).
            connection_string: Azure Storage connection string (legacy auth).
            use_managed_identity: If True, use DefaultAzureCredential.
        """
        self.container_name = container_name
        self.blob_name = blob_name

        try:
            if use_managed_identity:
                if not account_name:
                    raise StorageError(
                        "AZURE_STORAGE_ACCOUNT_NAME is required when using managed identity"
                    )
                account_url = f"https://{account_name}.blob.core.windows.net"
                credential = DefaultAzureCredential()
                self.blob_service_client = BlobServiceClient(
                    account_url=account_url,
                    credential=credential,
                )
                logger.info(
                    f"AzureBlobStorageAdapter using managed identity for {account_name}"
                )
            else:
                if not connection_string:
                    raise StorageError(
                        "AZURE_STORAGE_CONNECTION_STRING is required when not using managed identity"
                    )
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    connection_string
                )
                logger.info("AzureBlobStorageAdapter using connection string")

            self.container_client = self.blob_service_client.get_container_client(
                container_name
            )
            self.blob_client = self.container_client.get_blob_client(blob_name)
            logger.info(
                f"AzureBlobStorageAdapter initialized for {container_name}/{blob_name}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Azure Blob client: {e}")
            raise StorageError(f"Cannot connect to Azure Blob Storage: {e}") from e

    def _read_data(self) -> list[dict]:
        """Read services from Azure Blob Storage.

        Returns:
            List of service dictionaries.

        Raises:
            StorageError: If blob cannot be read or parsed.
        """
        try:
            if not self.blob_client.exists():
                logger.warning(f"Blob not found: {self.blob_name}, returning empty list")
                return []

            download = self.blob_client.download_blob()
            content = download.readall().decode("utf-8")
            data = json.loads(content)

            # Handle both {"services": [...]} and [...] formats
            if isinstance(data, dict) and "services" in data:
                return data["services"]
            if isinstance(data, list):
                return data
            raise StorageError(f"Unexpected JSON structure in blob {self.blob_name}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from blob: {e}")
            raise StorageError(f"Invalid JSON in blob {self.blob_name}") from e
        except Exception as e:
            logger.error(f"Failed to read blob: {e}")
            raise StorageError(f"Cannot read blob {self.blob_name}") from e

    def _write_data(self, services: list[dict]) -> None:
        """Write services to Azure Blob Storage.

        Args:
            services: List of service dictionaries to write.

        Raises:
            StorageError: If blob cannot be written.
        """
        try:
            content = json.dumps({"services": services}, indent=4, ensure_ascii=False)
            self.blob_client.upload_blob(content, overwrite=True)
            logger.debug(f"Wrote {len(services)} services to blob {self.blob_name}")
        except Exception as e:
            logger.error(f"Failed to write blob: {e}")
            raise StorageError(f"Cannot write blob {self.blob_name}") from e

    def list_services(
        self,
        category: str | None = None,
        search: str | None = None,
    ) -> list[Service]:
        """List all services, optionally filtered."""
        with tracer.start_as_current_span("storage.list_services") as span:
            span.set_attribute("storage.type", "azure_blob")
            span.set_attribute("storage.container", self.container_name)
            span.set_attribute("storage.blob", self.blob_name)
            if category:
                span.set_attribute("filter.category", category)
            if search:
                span.set_attribute("filter.search", search)

            try:
                services = self._read_data()
                result = []

                for svc in services:
                    # Apply category filter
                    if category and svc.get("category", "").lower() != category.lower():
                        continue

                    # Apply search filter
                    if search:
                        search_lower = search.lower()
                        name_match = search_lower in svc.get("service", "").lower()
                        desc_match = search_lower in svc.get("description", "").lower()
                        if not (name_match or desc_match):
                            continue

                    result.append(Service(**svc))

                span.set_attribute("result.count", len(result))
                return result
            except Exception as e:
                span.set_status(trace.StatusCode.ERROR, str(e))
                span.record_exception(e)
                raise

    def get_service(self, service_name: str) -> Service:
        """Get a single service by name."""
        with tracer.start_as_current_span("storage.get_service") as span:
            span.set_attribute("storage.type", "azure_blob")
            span.set_attribute("service.name", service_name)

            try:
                services = self._read_data()

                for svc in services:
                    if svc.get("service") == service_name:
                        span.set_attribute("result.found", True)
                        return Service(**svc)

                span.set_attribute("result.found", False)
                raise ServiceNotFoundError(f"Service not found: {service_name}")
            except ServiceNotFoundError:
                raise
            except Exception as e:
                span.set_status(trace.StatusCode.ERROR, str(e))
                span.record_exception(e)
                raise

    def create_service(self, service: ServiceCreate) -> Service:
        """Create a new service."""
        with tracer.start_as_current_span("storage.create_service") as span:
            span.set_attribute("storage.type", "azure_blob")
            span.set_attribute("service.name", service.service)

            try:
                services = self._read_data()

                # Check for duplicate
                for svc in services:
                    if svc.get("service") == service.service:
                        span.set_attribute("result.duplicate", True)
                        raise DuplicateServiceError(f"Service already exists: {service.service}")

                # Add new service
                new_service = service.model_dump()
                services.append(new_service)
                self._write_data(services)

                span.set_attribute("result.created", True)
                logger.info(f"Created service: {service.service}")
                return Service(**new_service)
            except DuplicateServiceError:
                raise
            except Exception as e:
                span.set_status(trace.StatusCode.ERROR, str(e))
                span.record_exception(e)
                raise

    def update_service(self, service_name: str, update: ServiceUpdate) -> Service:
        """Update an existing service."""
        with tracer.start_as_current_span("storage.update_service") as span:
            span.set_attribute("storage.type", "azure_blob")
            span.set_attribute("service.name", service_name)
            if update.service:
                span.set_attribute("service.new_name", update.service)

            try:
                services = self._read_data()
                found_index = None

                for i, svc in enumerate(services):
                    if svc.get("service") == service_name:
                        found_index = i
                        break

                if found_index is None:
                    span.set_attribute("result.found", False)
                    raise ServiceNotFoundError(f"Service not found: {service_name}")

                # Check if new name conflicts with existing service
                if update.service and update.service != service_name:
                    for svc in services:
                        if svc.get("service") == update.service:
                            span.set_attribute("result.duplicate", True)
                            raise DuplicateServiceError(f"Service already exists: {update.service}")

                # Apply updates (only non-None fields)
                update_data = update.model_dump(exclude_none=True)
                services[found_index].update(update_data)
                self._write_data(services)

                span.set_attribute("result.updated", True)
                logger.info(f"Updated service: {service_name}")
                return Service(**services[found_index])
            except (ServiceNotFoundError, DuplicateServiceError):
                raise
            except Exception as e:
                span.set_status(trace.StatusCode.ERROR, str(e))
                span.record_exception(e)
                raise

    def delete_service(self, service_name: str) -> None:
        """Delete a service."""
        with tracer.start_as_current_span("storage.delete_service") as span:
            span.set_attribute("storage.type", "azure_blob")
            span.set_attribute("service.name", service_name)

            try:
                services = self._read_data()
                original_count = len(services)

                services = [svc for svc in services if svc.get("service") != service_name]

                if len(services) == original_count:
                    span.set_attribute("result.found", False)
                    raise ServiceNotFoundError(f"Service not found: {service_name}")

                self._write_data(services)
                span.set_attribute("result.deleted", True)
                logger.info(f"Deleted service: {service_name}")
            except ServiceNotFoundError:
                raise
            except Exception as e:
                span.set_status(trace.StatusCode.ERROR, str(e))
                span.record_exception(e)
                raise


def get_storage_adapter(settings: "Settings") -> StorageAdapter:
    """Factory function to create the appropriate storage adapter.

    Args:
        settings: Application settings.

    Returns:
        StorageAdapter: Configured storage adapter instance.

    Raises:
        StorageError: If adapter cannot be created.
    """
    if settings.storage_type == "local":
        logger.info("Using LocalFileStorageAdapter")
        return LocalFileStorageAdapter(settings.local_data_path)

    if settings.storage_type == "azure":
        logger.info("Using AzureBlobStorageAdapter")
        return AzureBlobStorageAdapter(
            container_name=settings.azure_storage_container_name,
            blob_name=settings.azure_storage_blob_name,
            account_name=settings.azure_storage_account_name,
            connection_string=settings.azure_storage_connection_string or None,
            use_managed_identity=settings.azure_storage_use_managed_identity,
        )

    raise StorageError(f"Unknown storage type: {settings.storage_type}")
