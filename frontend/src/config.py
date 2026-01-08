"""Frontend configuration module.

Loads configuration from environment variables with sensible defaults
for local development.
"""

import os


class Config:
    """Frontend configuration loaded from environment variables."""

    # API settings
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")
    API_V1_PREFIX: str = "/api/v1"

    # Application Insights (optional)
    APPLICATIONINSIGHTS_CONNECTION_STRING: str = os.getenv(
        "APPLICATIONINSIGHTS_CONNECTION_STRING", ""
    )

    # UI settings
    PAGE_TITLE: str = "Azure Service Catalog"
    PAGE_ICON: str = "☁️"
    LAYOUT: str = "wide"

    @classmethod
    def get_api_url(cls, endpoint: str) -> str:
        """Build full API URL for an endpoint.

        Args:
            endpoint: API endpoint path (e.g., "/services").

        Returns:
            Full URL including base URL and API prefix.
        """
        base = cls.API_BASE_URL.rstrip("/")
        prefix = cls.API_V1_PREFIX.rstrip("/")
        endpoint = endpoint.lstrip("/")
        return f"{base}{prefix}/{endpoint}"


# Singleton instance
config = Config()
