# Data Model: Azure Monitor OpenTelemetry Integration

**Feature**: 002-azure-otel-telemetry  
**Date**: 2026-01-12

## Overview

This feature does not introduce new domain entities but defines telemetry data structures emitted to Azure Application Insights. These structures follow OpenTelemetry semantic conventions.

## Telemetry Entities

### Trace

Represents a complete request flow across services.

| Attribute | Type | Description |
|-----------|------|-------------|
| `trace_id` | string (32 hex) | Unique identifier for the distributed trace |
| `parent_id` | string (16 hex) | Parent span ID (null for root spans) |
| `cloud.role.name` | string | Service identifier: `azure-service-catalog-backend` or `azure-service-catalog-frontend` |
| `cloud.role.instance` | string | Instance identifier (auto-detected) |

### Span

Represents a single operation within a trace.

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | string | Operation name (e.g., `GET /api/v1/services`, `storage.list_services`) |
| `kind` | enum | `SERVER`, `CLIENT`, `INTERNAL` |
| `start_time` | timestamp | Operation start |
| `end_time` | timestamp | Operation end |
| `status` | enum | `OK`, `ERROR`, `UNSET` |
| `attributes` | dict | Operation-specific key-value pairs |

### HTTP Server Span Attributes (Backend)

Auto-instrumented for FastAPI requests.

| Attribute | Type | Example |
|-----------|------|---------|
| `http.method` | string | `GET`, `POST`, `PUT`, `DELETE` |
| `http.url` | string | `/api/v1/services` |
| `http.status_code` | int | `200`, `404`, `500` |
| `http.route` | string | `/api/v1/services/{service_name}` |

### HTTP Client Span Attributes (Frontend)

Auto-instrumented for httpx requests to backend.

| Attribute | Type | Example |
|-----------|------|---------|
| `http.method` | string | `GET` |
| `http.url` | string | `https://backend.azurewebsites.net/api/v1/services` |
| `http.status_code` | int | `200` |

### Storage Span Attributes (Custom)

Manually instrumented for storage operations.

| Attribute | Type | Example |
|-----------|------|---------|
| `storage.type` | string | `azure_blob`, `local_file` |
| `storage.operation` | string | `list`, `get`, `create`, `update`, `delete` |
| `storage.container` | string | `services` |
| `result.count` | int | Number of entities returned (for list operations) |
| `service.name` | string | Service name being operated on |

### Exception Telemetry

Captured automatically for unhandled exceptions.

| Attribute | Type | Description |
|-----------|------|-------------|
| `exception.type` | string | Exception class name |
| `exception.message` | string | Exception message |
| `exception.stacktrace` | string | Full stack trace |

## Cloud Role Mapping

| Component | `OTEL_SERVICE_NAME` | Application Map Node |
|-----------|---------------------|---------------------|
| FastAPI Backend | `azure-service-catalog-backend` | Backend API |
| Streamlit Frontend | `azure-service-catalog-frontend` | Frontend Web |

## Log Correlation

All logs emitted through Python `logging` module are automatically correlated with active traces via:

| Log Field | OpenTelemetry Context |
|-----------|----------------------|
| `trace_id` | Current trace ID |
| `span_id` | Current span ID |
| `trace_flags` | Sampling decision |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | Yes | App Insights connection string |
| `OTEL_SERVICE_NAME` | Yes | Cloud role name for this component |
| `OTEL_RESOURCE_ATTRIBUTES` | No | Additional resource attributes (optional) |

## Validation Rules

1. **OTEL_SERVICE_NAME**: Must be set to non-empty string before `configure_azure_monitor()` is called
2. **APPLICATIONINSIGHTS_CONNECTION_STRING**: If not set, telemetry is disabled (graceful degradation)
3. **Custom Spans**: Must have unique names within the operation context
4. **Span Attributes**: Values must be string, int, float, or bool (no complex objects)

## State Transitions

Not applicable—telemetry entities are write-only (emitted to Application Insights).
