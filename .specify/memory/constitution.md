<!--
================================================================================
SYNC IMPACT REPORT
================================================================================
Version Change: 1.0.0 → 1.1.0 (MINOR - new principle added)

Modified Principles: None

Added Sections:
  - Principle VI: Test-Driven Quality (new testing mandate)

Removed Sections: None

Templates Requiring Updates:
  - .specify/templates/plan-template.md ✅ compatible (Testing context exists)
  - .specify/templates/spec-template.md ✅ compatible (User Scenarios & Testing section exists)
  - .specify/templates/tasks-template.md ✅ compatible (test phases documented)

Follow-up TODOs: None
================================================================================
-->

# Azure Demo App Constitution

## Core Principles

### I. Service Separation

All functionality MUST be implemented as distinct, deployable microservices:

- **Frontend service**: Streamlit-based web UI; handles user interaction only
- **Backend service**: FastAPI-based REST API; handles all business logic and data operations
- **Storage layer**: Azure Blob Storage; single source of truth for persistent data

Services MUST communicate only via documented HTTP APIs. Direct database/storage access from frontend is PROHIBITED.

### II. API-First Design

Every backend capability MUST be exposed through a versioned REST API:

- All endpoints documented with OpenAPI/Swagger specifications
- Request/response schemas defined using Pydantic models
- API versioning via URL prefix (e.g., `/api/v1/`)
- Consistent error response format across all endpoints

Frontend MUST consume backend exclusively through these documented APIs.

### III. Configuration Over Code

Environment-specific settings MUST NOT be hardcoded:

- Azure connection strings, storage account names, and URLs MUST use environment variables
- Local development MUST work with `.env` files or Azure CLI authentication
- Production deployments MUST use Azure App Configuration or Key Vault references
- Sensitive credentials MUST NEVER appear in source code or logs
- **Azure services MUST authenticate using system-assigned managed identities** (not connection strings or access keys) for production deployments
- Storage accounts MUST have `shared_access_key_enabled = false` when managed identity is used

### IV. Observability

All services MUST implement structured logging and health monitoring:

- Use Python `logging` module with JSON-formatted output for production
- Health check endpoints (`/health`) MUST be exposed by each service
- Azure Application Insights integration for production telemetry
- Request IDs MUST propagate across service boundaries for tracing

### V. Simplicity First

Prefer simple, maintainable solutions over complex abstractions:

- YAGNI (You Aren't Gonna Need It): implement only what is required now
- No premature optimization; measure before optimizing
- Standard library and well-established packages preferred over custom implementations
- Code SHOULD be readable by developers unfamiliar with the codebase

### VI. Test-Driven Quality

All production code MUST have accompanying tests:

- Unit tests MUST cover all business logic and service layer functions
- Integration tests MUST verify API endpoints and cross-service communication
- Tests MUST be written before or alongside implementation (test-first encouraged)
- Minimum code coverage threshold: 80% for all services
- Tests MUST be deterministic—no flaky tests permitted in the main branch
- Contract tests MUST validate API schemas against OpenAPI specifications
- Test failures MUST block PR merges; no exceptions without documented justification

**Rationale**: Tests are the executable specification of system behavior. Without tests, refactoring becomes risky, regressions go undetected, and confidence in deployments diminishes.

## Technology Stack

The following technologies are MANDATORY for this project:

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Frontend | Streamlit | 1.x | Web UI framework |
| Backend | FastAPI | 0.100+ | REST API framework |
| Storage | Azure Blob Storage | - | Persistent data (data.json) |
| Language | Python | 3.11+ | All services |
| Testing | pytest | 7.x+ | Unit and integration tests |
| Deployment | Azure App Service | - | Hosting both services |

**Prohibited**: Direct SQL databases, GraphQL, alternative web frameworks.

## Development Workflow

### Code Organization

```text
frontend/
├── app.py                # Streamlit entry point
├── components/           # Reusable UI components
├── services/             # Backend API client
└── tests/

backend/
├── main.py               # FastAPI entry point
├── api/                  # Route handlers
│   └── v1/
├── models/               # Pydantic schemas
├── services/             # Business logic
├── storage/              # Azure Blob operations
└── tests/
```

### Quality Gates

Before any PR merge:

1. All tests MUST pass (`pytest` with minimum 80% coverage)
2. Type hints MUST be present on all public functions
3. Linting MUST pass (ruff or flake8)
4. API changes MUST update OpenAPI documentation

### Local Development

- Backend: `uvicorn backend.main:app --reload`
- Frontend: `streamlit run frontend/app.py`
- Storage: Use Azurite emulator or actual Azure Blob with dev credentials

## Governance

This constitution supersedes all other development practices for this project.

**Amendment Process**:

1. Propose change via PR modifying this document
2. Document rationale and migration plan for breaking changes
3. Update dependent templates if principles change
4. Increment version according to semantic versioning

**Compliance**:

- All PRs MUST verify adherence to these principles
- Violations require explicit justification in PR description
- Recurring violations trigger constitution review

**Version**: 1.1.0 | **Ratified**: 2026-01-08 | **Last Amended**: 2026-01-08
