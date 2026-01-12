# Research: Azure Monitor OpenTelemetry Integration

**Feature**: 002-azure-otel-telemetry  
**Date**: 2026-01-12  
**Status**: Complete

## Research Tasks

### 1. Azure Monitor OpenTelemetry SDK Configuration

**Task**: Research best practices for `azure-monitor-opentelemetry` package configuration in Python applications.

**Decision**: Use `configure_azure_monitor()` as the single entry point with environment variables.

**Rationale**:
- The Azure Monitor OpenTelemetry Distro (`azure-monitor-opentelemetry`) is a meta-package that bundles:
  - `opentelemetry-instrumentation-*` packages for auto-instrumentation
  - `azure-monitor-opentelemetry-exporter` for Azure Monitor export
  - Proper semantic conventions and resource detection
- Single function call `configure_azure_monitor()` handles all setup
- Environment variables (`OTEL_SERVICE_NAME`, `APPLICATIONINSIGHTS_CONNECTION_STRING`) are the recommended configuration method

**Alternatives considered**:
- Manual OpenTelemetry SDK setup with Azure exporter: Rejected—more complex, no Live Metrics support, requires manual instrumentation registration
- Direct `azure-monitor-opentelemetry-exporter` only: Rejected—missing auto-instrumentation and convenience wrappers

**Key Configuration**:
```python
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor(
    enable_live_metrics=True,  # Real-time monitoring
    sampling_ratio=1.0,        # 100% sampling (capture all requests)
)
```

### 2. Cloud Role Name Configuration

**Task**: Research how to set distinct cloud role names for Application Map visualization.

**Decision**: Use `OTEL_SERVICE_NAME` environment variable per component.

**Rationale**:
- OpenTelemetry semantic convention: `service.name` resource attribute
- Azure Monitor maps `OTEL_SERVICE_NAME` to cloud role name
- Environment variable approach avoids code changes when renaming services
- Terraform can manage the values centrally

**Alternatives considered**:
- `resource_attributes` parameter in `configure_azure_monitor()`: Rejected—ties configuration to code
- `OTEL_RESOURCE_ATTRIBUTES`: Works but more verbose than dedicated `OTEL_SERVICE_NAME`

**Implementation**:
- Backend: `OTEL_SERVICE_NAME=azure-service-catalog-backend`
- Frontend: `OTEL_SERVICE_NAME=azure-service-catalog-frontend`

### 3. FastAPI Auto-Instrumentation

**Task**: Research FastAPI instrumentation with Azure Monitor OpenTelemetry.

**Decision**: Rely on auto-instrumentation included in the distro; no manual setup needed.

**Rationale**:
- `azure-monitor-opentelemetry` automatically installs and enables:
  - `opentelemetry-instrumentation-fastapi` - HTTP server spans
  - `opentelemetry-instrumentation-httpx` - HTTP client spans (for API calls)
  - `opentelemetry-instrumentation-logging` - Log correlation
- Trace context propagation handled automatically via W3C Trace Context headers

**Alternatives considered**:
- Manual instrumentation registration: Rejected—unnecessary complexity
- Custom middleware: Rejected—duplicates built-in functionality

### 4. Streamlit Telemetry Patterns

**Task**: Research telemetry integration for Streamlit applications.

**Decision**: Configure Azure Monitor before Streamlit imports; use logging integration for visibility.

**Rationale**:
- Streamlit is not a traditional WSGI/ASGI framework—no server-side instrumentation hook
- Telemetry focuses on:
  - Logging (user actions, errors)
  - HTTP client spans (API calls to backend via httpx)
  - Exception tracking
- `configure_azure_monitor()` must be called before any Streamlit code imports to ensure proper instrumentation

**Alternatives considered**:
- Custom Streamlit callbacks for spans: Rejected—overly complex, minimal benefit
- Streamlit Cloud telemetry: Not applicable—using Azure App Service

**Implementation pattern**:
```python
# telemetry.py - imported FIRST
from azure.monitor.opentelemetry import configure_azure_monitor
configure_azure_monitor(...)

# app.py
from src.telemetry import configure_telemetry
configure_telemetry()  # Must be before streamlit import

import streamlit as st
```

### 5. Custom Span Instrumentation for Storage

**Task**: Research patterns for adding custom spans to storage operations.

**Decision**: Use OpenTelemetry tracer API with `start_as_current_span()`.

**Rationale**:
- Azure Blob Storage SDK has built-in instrumentation via `azure-core-tracing-opentelemetry`
- Custom spans needed for:
  - Business-level operations (list_services, get_service, create_service, etc.)
  - Local file storage adapter (no auto-instrumentation)
- Span attributes should include operation type, entity count, service names

**Implementation pattern**:
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def list_services(self, ...):
    with tracer.start_as_current_span("storage.list_services") as span:
        span.set_attribute("storage.type", "azure_blob")
        # ... operation
        span.set_attribute("result.count", len(services))
        return services
```

**Alternatives considered**:
- Decorator-based instrumentation: Rejected—less control over span attributes
- Separate instrumentation module: Rejected—spans belong with operations

### 6. Graceful Degradation Without Connection String

**Task**: Research behavior when Application Insights is not configured.

**Decision**: Check for connection string before calling `configure_azure_monitor()`; log warning if missing.

**Rationale**:
- Local development may not have App Insights configured
- Application must function normally without telemetry
- Warning log ensures developers are aware telemetry is disabled

**Implementation**:
```python
import os
import logging

logger = logging.getLogger(__name__)

def configure_telemetry():
    connection_string = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if not connection_string:
        logger.warning("APPLICATIONINSIGHTS_CONNECTION_STRING not set - telemetry disabled")
        return
    
    configure_azure_monitor(
        enable_live_metrics=True,
        sampling_ratio=1.0,
    )
    logger.info("Azure Monitor telemetry configured")
```

### 7. OpenCensus Removal

**Task**: Identify OpenCensus usage and removal strategy.

**Decision**: Remove all `opencensus-ext-azure` imports and configuration; replace with Azure Monitor OpenTelemetry.

**Findings in current codebase**:

**backend/src/main.py** (lines 30-51):
```python
# CURRENT - TO BE REMOVED
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.tracer import Tracer
```

**frontend/src/app.py** (lines 24-37):
```python
# CURRENT - TO BE REMOVED
from opencensus.ext.azure.log_exporter import AzureLogHandler
```

**Dependencies to remove**:
- `backend/pyproject.toml`: Remove `opencensus-ext-azure>=1.1.13`
- `frontend/pyproject.toml`: Remove `opencensus-ext-azure>=1.1.13`

**Rationale for removal**:
- OpenCensus is deprecated (project merged into OpenTelemetry)
- Incompatible with Azure Monitor health model
- Not supported for Azure Service Groups integration

### 8. Testing Strategy

**Task**: Research testing approaches for telemetry modules.

**Decision**: Mock `configure_azure_monitor()` in unit tests; integration tests verify no errors in real calls.

**Rationale**:
- Unit tests should not require Azure credentials
- Telemetry module is thin wrapper—test that it calls configuration correctly
- Integration tests verify application starts without telemetry errors

**Test patterns**:
```python
# Unit test
from unittest.mock import patch

def test_configure_telemetry_with_connection_string():
    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test"}):
        with patch("azure.monitor.opentelemetry.configure_azure_monitor") as mock_configure:
            configure_telemetry()
            mock_configure.assert_called_once_with(
                enable_live_metrics=True,
                sampling_ratio=1.0,
            )

def test_configure_telemetry_without_connection_string(caplog):
    with patch.dict(os.environ, {}, clear=True):
        configure_telemetry()
        assert "telemetry disabled" in caplog.text
```

## Summary

All research tasks completed. Key decisions:

| Topic | Decision |
|-------|----------|
| SDK | `azure-monitor-opentelemetry` with `configure_azure_monitor()` |
| Cloud Role | `OTEL_SERVICE_NAME` environment variable |
| FastAPI | Auto-instrumentation (included in distro) |
| Streamlit | Configure before imports; logging + HTTP client spans |
| Storage Spans | OpenTelemetry tracer API with `start_as_current_span()` |
| Graceful Degradation | Check env var, log warning, continue without telemetry |
| OpenCensus | Full removal from dependencies and code |
| Testing | Mock SDK in unit tests; verify startup in integration |

## References

- [Enable Azure Monitor OpenTelemetry for Python](https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-enable?tabs=python)
- [Configure Azure Monitor OpenTelemetry](https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-configuration?tabs=python)
- [Set Cloud Role Name](https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-configuration?tabs=python#set-the-cloud-role-name-and-the-cloud-role-instance)
- [OpenTelemetry Python Manual Instrumentation](https://opentelemetry.io/docs/languages/python/instrumentation/)
- [azure-monitor-opentelemetry PyPI](https://pypi.org/project/azure-monitor-opentelemetry/)
