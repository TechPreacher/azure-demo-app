# Implementation Plan: Telemetry Simulation Buttons

**Branch**: `003-telemetry-simulation-buttons` | **Date**: 2026-01-12 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-telemetry-simulation-buttons/spec.md`

## Summary

Add two frontend buttons ("Latency" and "Error") that trigger backend simulation endpoints to test telemetry capture in Application Insights. The latency endpoint introduces a random 10-20 second delay; the error endpoint returns HTTP 500 with rotating realistic error messages. Both endpoints are instrumented with OpenTelemetry for distributed tracing verification.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI 0.109+, Streamlit 1.30+, azure-monitor-opentelemetry 1.0+, httpx 0.26+  
**Storage**: N/A (no persistent storage required for simulation endpoints)  
**Testing**: pytest 7.4+, pytest-asyncio 0.23+  
**Target Platform**: Azure App Service (Linux)  
**Project Type**: Web application (frontend + backend)  
**Performance Goals**: Latency endpoint must support 10-20 second async sleep without blocking; Error endpoint must respond within 100ms  
**Constraints**: Frontend timeout must be ≥30 seconds for latency button; Async implementation required to prevent blocking  
**Scale/Scope**: Demo application; single concurrent user expected; 2 new endpoints, 2 API client methods, 1 UI section

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Service Separation | ✅ PASS | Frontend buttons call backend API endpoints; no direct storage access |
| II. API-First Design | ✅ PASS | New endpoints follow `/api/v1/` versioning; Pydantic response models defined |
| III. Configuration Over Code | ✅ PASS | No hardcoded values; inherits existing telemetry config |
| IV. Observability | ✅ PASS | Both endpoints instrumented with OpenTelemetry; cloud role names already set |
| V. Simplicity First | ✅ PASS | Minimal implementation; uses existing patterns (FastAPI router, httpx client) |
| VI. Test-Driven Quality | ✅ PASS | Unit and integration tests planned; 80% coverage maintained |

**Gate Status**: ✅ ALL GATES PASS - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/003-telemetry-simulation-buttons/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI schemas)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   ├── routes.py         # Existing - include simulation router
│   │   └── simulation.py     # NEW - simulation endpoints
│   ├── models/
│   │   └── simulation.py     # NEW - response models
│   └── main.py               # Existing - register router
└── tests/
    ├── unit/
    │   └── test_simulation.py    # NEW - unit tests
    └── integration/
        └── test_simulation_api.py # NEW - integration tests

frontend/
├── src/
│   ├── api_client.py         # Existing - add simulation methods
│   └── app.py                # Existing - add simulation buttons
└── tests/
    └── test_api_client.py    # Existing - add simulation tests
```

**Structure Decision**: Web application structure (Option 2) - matches existing repository layout with separate `backend/` and `frontend/` directories.

## Complexity Tracking

> No violations identified. Feature follows existing patterns with minimal additions.
