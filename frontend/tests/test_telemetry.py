"""Tests for telemetry configuration module."""

import logging
from unittest.mock import MagicMock, patch

import pytest


class TestConfigureTelemetry:
    """Test cases for configure_telemetry function."""

    def test_configure_telemetry_without_connection_string(self, caplog):
        """Test that telemetry is disabled when connection string is not set."""
        with patch.dict("os.environ", {}, clear=True):
            # Re-import to get fresh module state
            from src.telemetry import configure_telemetry

            with caplog.at_level(logging.WARNING):
                configure_telemetry()

            assert "APPLICATIONINSIGHTS_CONNECTION_STRING not set" in caplog.text

    def test_configure_telemetry_with_connection_string(self, caplog):
        """Test that telemetry is configured when connection string is set."""
        mock_configure = MagicMock()
        test_conn_string = "InstrumentationKey=test-key;IngestionEndpoint=https://test.in.applicationinsights.azure.com/"

        with patch.dict("os.environ", {"APPLICATIONINSIGHTS_CONNECTION_STRING": test_conn_string}):
            with patch("azure.monitor.opentelemetry.configure_azure_monitor", mock_configure):
                from src.telemetry import configure_telemetry

                with caplog.at_level(logging.INFO):
                    configure_telemetry()

                mock_configure.assert_called_once_with(
                    enable_live_metrics=True,
                    sampling_ratio=1.0,
                )
                assert "Azure Monitor OpenTelemetry configured successfully" in caplog.text

    def test_configure_telemetry_handles_import_error(self, caplog):
        """Test that ImportError is handled gracefully."""
        test_conn_string = "InstrumentationKey=test-key"

        with patch.dict("os.environ", {"APPLICATIONINSIGHTS_CONNECTION_STRING": test_conn_string}):
            with patch.dict("sys.modules", {"azure.monitor.opentelemetry": None}):
                # Force ImportError by removing module
                import sys

                original_modules = sys.modules.copy()
                sys.modules["azure"] = None
                sys.modules["azure.monitor"] = None
                sys.modules["azure.monitor.opentelemetry"] = None

                try:
                    # Create a fresh import that will fail
                    from src.telemetry import configure_telemetry

                    with caplog.at_level(logging.WARNING):
                        configure_telemetry()

                    assert "not installed" in caplog.text or "telemetry disabled" in caplog.text.lower()
                finally:
                    # Restore modules
                    for key in ["azure", "azure.monitor", "azure.monitor.opentelemetry"]:
                        if key in original_modules:
                            sys.modules[key] = original_modules[key]
                        elif key in sys.modules:
                            del sys.modules[key]

    def test_configure_telemetry_handles_configuration_error(self, caplog):
        """Test that configuration errors are handled gracefully."""
        test_conn_string = "InstrumentationKey=test-key"

        def raise_error(*args, **kwargs):
            raise RuntimeError("Configuration failed")

        with patch.dict("os.environ", {"APPLICATIONINSIGHTS_CONNECTION_STRING": test_conn_string}):
            with patch("azure.monitor.opentelemetry.configure_azure_monitor", side_effect=raise_error):
                from src.telemetry import configure_telemetry

                with caplog.at_level(logging.ERROR):
                    configure_telemetry()

                assert "Failed to configure" in caplog.text or "Configuration failed" in caplog.text

    def test_configure_telemetry_with_empty_connection_string(self, caplog):
        """Test that empty connection string is treated as not set."""
        with patch.dict("os.environ", {"APPLICATIONINSIGHTS_CONNECTION_STRING": ""}):
            from src.telemetry import configure_telemetry

            with caplog.at_level(logging.WARNING):
                configure_telemetry()

            assert "APPLICATIONINSIGHTS_CONNECTION_STRING not set" in caplog.text
