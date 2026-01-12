"""Telemetry configuration for Azure Service Catalog Frontend.

Configures Azure Monitor OpenTelemetry SDK for automatic instrumentation
of the Streamlit frontend with Application Insights integration.
"""

import logging
import os

logger = logging.getLogger(__name__)


def configure_telemetry() -> None:
    """Configure Azure Monitor OpenTelemetry for the frontend.

    This function initializes the Azure Monitor OpenTelemetry SDK when
    the APPLICATIONINSIGHTS_CONNECTION_STRING environment variable is set.
    The SDK provides automatic instrumentation for HTTP requests and logging.

    Cloud role name is set via the OTEL_SERVICE_NAME environment variable
    (defaults to 'azure-service-catalog-frontend' in Azure App Service).

    Configuration:
        - enable_live_metrics: True (real-time performance monitoring)
        - sampling_ratio: 1.0 (100% of requests captured)

    When telemetry is not configured (no connection string), the function
    logs a warning and returns without error, allowing the application
    to run without telemetry.
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
        logger.error(f"Failed to configure Azure Monitor OpenTelemetry: {e}")
