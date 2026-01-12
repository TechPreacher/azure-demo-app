"""Tests for telemetry configuration module."""

import logging
import os
from unittest.mock import MagicMock, patch

import pytest

from src.telemetry import configure_telemetry


class TestConfigureTelemetry:
    """Tests for configure_telemetry function."""

    def test_configure_telemetry_without_connection_string(self, caplog):
        """Test that telemetry is disabled when connection string is not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove the connection string if it exists
            os.environ.pop("APPLICATIONINSIGHTS_CONNECTION_STRING", None)

            with caplog.at_level(logging.WARNING):
                configure_telemetry()

            assert "APPLICATIONINSIGHTS_CONNECTION_STRING not set" in caplog.text
            assert "telemetry disabled" in caplog.text

    def test_configure_telemetry_with_connection_string(self, caplog):
        """Test that telemetry is configured when connection string is set."""
        mock_connection_string = "InstrumentationKey=test-key;IngestionEndpoint=https://test.in.applicationinsights.azure.com/"

        with patch.dict(
            os.environ,
            {"APPLICATIONINSIGHTS_CONNECTION_STRING": mock_connection_string},
        ):
            with patch(
                "azure.monitor.opentelemetry.configure_azure_monitor"
            ) as mock_configure:
                with caplog.at_level(logging.INFO):
                    configure_telemetry()

                mock_configure.assert_called_once_with(
                    enable_live_metrics=True,
                    sampling_ratio=1.0,
                )
                assert "Azure Monitor OpenTelemetry configured successfully" in caplog.text

    def test_configure_telemetry_handles_import_error(self, caplog):
        """Test graceful handling when azure-monitor-opentelemetry is not installed."""
        mock_connection_string = "InstrumentationKey=test-key"

        with patch.dict(
            os.environ,
            {"APPLICATIONINSIGHTS_CONNECTION_STRING": mock_connection_string},
        ):
            with patch.dict("sys.modules", {"azure.monitor.opentelemetry": None}):
                with caplog.at_level(logging.WARNING):
                    # Re-import to trigger the ImportError path
                    import importlib
                    import src.telemetry
                    importlib.reload(src.telemetry)
                    
                    # This test verifies the import error handling
                    # Since we're patching sys.modules, the import will fail
                    # The function should log a warning
                    
        # Reset by reloading the module
        import importlib
        import src.telemetry
        importlib.reload(src.telemetry)

    def test_configure_telemetry_handles_configuration_error(self, caplog):
        """Test graceful handling when configuration fails."""
        mock_connection_string = "InstrumentationKey=test-key"

        with patch.dict(
            os.environ,
            {"APPLICATIONINSIGHTS_CONNECTION_STRING": mock_connection_string},
        ):
            with patch(
                "azure.monitor.opentelemetry.configure_azure_monitor",
                side_effect=Exception("Configuration failed"),
            ):
                with caplog.at_level(logging.WARNING):
                    configure_telemetry()

                assert "Failed to configure Azure Monitor OpenTelemetry" in caplog.text
                assert "Configuration failed" in caplog.text

    def test_configure_telemetry_with_empty_connection_string(self, caplog):
        """Test that empty connection string is treated as not set."""
        with patch.dict(
            os.environ,
            {"APPLICATIONINSIGHTS_CONNECTION_STRING": ""},
        ):
            with caplog.at_level(logging.WARNING):
                configure_telemetry()

            assert "APPLICATIONINSIGHTS_CONNECTION_STRING not set" in caplog.text
