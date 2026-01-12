# Implementation Plan: Azure Monitor OpenTelemetry Integration

**Branch**: `002-azure-otel-telemetry` | **Date**: 2026-01-12 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-azure-otel-telemetry/spec.md`

## Summary

Replace deprecated OpenCensus telemetry with Azure Monitor OpenTelemetry SDK across all application components (frontend, backend, storage layer). Each component emits traces, logs, and exceptions to Azure Application Insights with distinct cloud role names (`azure-service-catalog-backend`, `azure-service-catalog-frontend`) for Application Map visualization and Azure Service Groups health model compatibility.

**Technical approach**: Use `configure_azure_monitor()` as single entry point, set cloud role via `OTEL_SERVICE_NAME` environment variable, add custom spans to storage operations, enable Live Metrics with 100% sampling.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI 0.109+, Streamlit 1.30+, azure-monitor-opentelemetry (new), httpx 0.26+  
**Storage**: Azure Blob Storage (via azure-storage-blob with managed identity)  
**Testing**: pytest 7.x with pytest-cov, pytest-asyncio  
**Target Platform**: Azure App Service Linux (Python 3.11)  
**Project Type**: Web application (frontend + backend)  
**Performance Goals**: Telemetry must add <5ms latency per request  
**Constraints**: 100% sampling ratio, Live Metrics enabled, no OpenCensus dependencies  
**Scale/Scope**: 2 App Services, 1 Application Insights resource, single tenant

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Service Separation | ✅ PASS | Frontend and backend remain separate services |
| II. API-First Design | ✅ PASS | No API changes required—telemetry is cross-cutting |
| III. Configuration Over Code | ✅ PASS | Uses `OTEL_SERVICE_NAME` and `APPLICATIONINSIGHTS_CONNECTION_STRING` env vars |
| IV. Observability | ✅ PASS | Implements mandatory telemetry requirements from constitution v1.2.0 |
| V. Simplicity First | ✅ PASS | Uses single `configure_azure_monitor()` call—no custom abstractions |
| VI. Test-Driven Quality | ✅ PASS | Telemetry module testable with mocked SDK; coverage maintained |
| Technology Stack | ✅ PASS | Uses mandated `azure-monitor-opentelemetry` package |

**Pre-design gate**: ✅ PASSED  
**Post-design gate**: ✅ PASSED (verified after Phase 1 design)

- All artifacts follow constitution principles
- `azure-monitor-opentelemetry` is the only telemetry SDK
- Configuration via environment variables only
- No API contract changes

## Project Structure

### Documentation (this feature)

```text
specs/002-azure-otel-telemetry/
├── plan.md              # This file
├── research.md          # Phase 0 output - SDK best practices
├── data-model.md        # Phase 1 output - telemetry entities
├── quickstart.md        # Phase 1 output - developer setup guide
├── contracts/           # Phase 1 output - N/A (no API changes)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py               # MODIFY: Replace OpenCensus with configure_azure_monitor()
│   ├── telemetry.py          # NEW: Telemetry configuration module
│   ├── api/
│   │   ├── routes.py
│   │   └── dependencies.py
│   ├── models/
│   │   └── service.py
│   └── services/
│       └── storage.py        # MODIFY: Add OpenTelemetry spans
├── pyproject.toml            # MODIFY: Remove opencensus, add azure-monitor-opentelemetry
└── tests/
    ├── unit/
    │   └── test_telemetry.py # NEW: Telemetry module tests
    └── integration/

frontend/
├── src/
│   ├── __init__.py
│   ├── app.py                # MODIFY: Replace OpenCensus with configure_azure_monitor()
│   ├── config.py
│   ├── telemetry.py          # NEW: Telemetry configuration module
│   ├── api_client.py
│   └── components/
├── pyproject.toml            # MODIFY: Remove opencensus, add azure-monitor-opentelemetry
└── tests/
    └── test_telemetry.py     # NEW: Telemetry module tests

infrastructure/
└── modules/
    └── app_service/
        └── main.tf           # MODIFY: Add OTEL_SERVICE_NAME env vars
```

**Structure Decision**: Web application structure with separate frontend and backend. Telemetry modules created at `src/telemetry.py` in each project for centralized configuration.

## Complexity Tracking

> No violations—design follows constitution principles without exceptions.
