"""Backend configuration module.

Loads configuration from environment variables with sensible defaults
for local development.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Storage configuration
    storage_type: Literal["local", "azure"] = "local"
    local_data_path: str = "../data/services.json"
    local_storage_path: str = "../data/services.json"  # Alias for compatibility

    # Azure Blob Storage settings (required when storage_type="azure")
    azure_storage_account_name: str = ""
    azure_storage_connection_string: str = ""  # Legacy: used if managed identity disabled
    azure_storage_container_name: str = "data"
    azure_storage_blob_name: str = "services.json"
    azure_storage_use_managed_identity: bool = False  # Set to True in Azure App Service

    # Application Insights (optional)
    applicationinsights_connection_string: str = ""

    # OpenTelemetry configuration (set via OTEL_SERVICE_NAME env var)
    otel_service_name: str = "azure-service-catalog-backend"

    # API settings
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:8501", "http://localhost:3000"]

    # Server settings
    debug: bool = True
    log_level: str = "INFO"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",  # Ignore extra env vars not defined in the model
    }


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings: Application settings loaded from environment.
    """
    return Settings()
