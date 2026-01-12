"""Azure Monitor OpenTelemetry configuration module.

Provides centralized telemetry configuration for the backend service.
Must be imported and called BEFORE any other application imports.
"""

import logging
import os

logger = logging.getLogger(__name__)


def configure_telemetry() -> None:
    """Configure Azure Monitor OpenTelemetry for the backend service.

    This function must be called at application startup BEFORE importing
    FastAPI or other application modules to ensure proper instrumentation.

    Configuration is done via environment variables:
    - APPLICATIONINSIGHTS_CONNECTION_STRING: Required for telemetry export
    - OTEL_SERVICE_NAME: Sets cloud role name (default: azure-service-catalog-backend)

    If APPLICATIONINSIGHTS_CONNECTION_STRING is not set, telemetry is disabled
    and a warning is logged. The application continues to function normally.
    """
    connection_string = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")

    if not connection_string:
        logger.warning(
            "APPLICATIONINSIGHTS_CONNECTION_STRING not set - telemetry disabled"
        )
        return

    try:
        from azure.monitor.opentelemetry import configure_azure_monitor

        configure_azure_monitor(
            enable_live_metrics=True,
            sampling_ratio=1.0,
        )
        logger.info("Azure Monitor OpenTelemetry configured successfully")
    except ImportError:
        logger.warning(
            "azure-monitor-opentelemetry not installed - telemetry disabled"
        )
    except Exception as e:
        logger.warning(f"Failed to configure Azure Monitor OpenTelemetry: {e}")
