# Feature Specification: Azure Monitor OpenTelemetry Integration

**Feature Branch**: `002-azure-otel-telemetry`  
**Created**: 2026-01-12  
**Status**: Draft  
**Input**: Implement Azure Monitor OpenTelemetry for all application components (frontend, backend, storage) with distinct cloud role names. The Azure Monitor OpenTelemetry Python SDK is MANDATORY to ensure compatibility with Azure Monitor health model and Azure Service Groups.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Backend API Telemetry with Cloud Role Name (Priority: P1)

As a developer/operator, I want the FastAPI backend to send telemetry (traces, logs, metrics) to Azure Monitor Application Insights with a distinct cloud role name "azure-service-catalog-backend" so that I can identify backend requests in the Application Map and troubleshoot API issues.

**Why this priority**: The backend is the core service handling all data operations. Without proper telemetry, debugging production issues is nearly impossible. This is the foundation for distributed tracing.

**Independent Test**: Can be tested by deploying only the backend, making API calls (e.g., GET /api/v1/services), and verifying telemetry appears in Application Insights with the correct cloud role name shown in the Application Map.

**Acceptance Scenarios**:

1. **Given** the backend is deployed with `APPLICATIONINSIGHTS_CONNECTION_STRING` and `OTEL_SERVICE_NAME=azure-service-catalog-backend` configured, **When** a user calls `GET /api/v1/services`, **Then** a trace with the request details appears in Application Insights Transaction Search within 5 minutes.
2. **Given** the backend is configured with OpenTelemetry, **When** viewing the Application Map in Azure Portal, **Then** the backend appears as a distinct node labeled "azure-service-catalog-backend".
3. **Given** an error occurs in the backend (e.g., storage unavailable), **When** the error is logged, **Then** the exception appears in Application Insights Failures view with full stack trace.
4. **Given** the backend receives a request with a correlation ID header, **When** processing the request, **Then** the trace includes the correlation ID for end-to-end tracing.

---

### User Story 2 - Frontend Streamlit Telemetry with Cloud Role Name (Priority: P2)

As a developer/operator, I want the Streamlit frontend to send telemetry to Azure Monitor Application Insights with a distinct cloud role name "azure-service-catalog-frontend" so that I can track user interactions and correlate frontend activity with backend calls.

**Why this priority**: Frontend telemetry enables understanding user behavior and correlating frontend requests with backend processing. It completes the distributed tracing picture.

**Independent Test**: Can be tested by deploying the frontend, navigating through the UI, and verifying telemetry appears in Application Insights with the "azure-service-catalog-frontend" cloud role name.

**Acceptance Scenarios**:

1. **Given** the frontend is deployed with `APPLICATIONINSIGHTS_CONNECTION_STRING` and `OTEL_SERVICE_NAME=azure-service-catalog-frontend` configured, **When** a user loads the main page, **Then** application logs appear in Application Insights with the frontend cloud role name.
2. **Given** the frontend is configured with OpenTelemetry, **When** viewing the Application Map in Azure Portal, **Then** the frontend appears as a distinct node labeled "azure-service-catalog-frontend" with a connection line to the backend.
3. **Given** the frontend makes an API call to the backend, **When** viewing the trace, **Then** the trace shows the complete request path from frontend to backend.

---

### User Story 3 - Storage Layer Telemetry (Priority: P3)

As a developer/operator, I want storage operations (Azure Blob Storage or local file access) to be instrumented with OpenTelemetry spans so that I can identify slow storage operations and understand data access patterns.

**Why this priority**: Storage is often a performance bottleneck. Instrumenting storage calls helps identify slow queries and understand data access patterns. This builds on top of the backend telemetry.

**Independent Test**: Can be tested by performing CRUD operations via the API and verifying that storage-specific spans appear as child spans in Application Insights traces.

**Acceptance Scenarios**:

1. **Given** the backend is processing a request that requires storage access, **When** the storage adapter reads from Azure Blob Storage, **Then** a child span "storage.list_services" or "storage.get_service" appears in the trace.
2. **Given** a storage operation fails (e.g., blob not found), **When** the exception is raised, **Then** the span is marked as failed with error details.
3. **Given** Azure Blob Storage instrumentation is enabled, **When** the Azure SDK makes HTTP calls, **Then** dependency telemetry shows Azure Storage as a dependency.

---

### Edge Cases

- What happens when Application Insights connection string is not configured? System should operate normally without telemetry, logging a warning at startup.
- What happens when Application Insights is temporarily unavailable? Telemetry should be cached locally and retried (up to 48 hours per Azure Monitor SDK default).
- How does system handle high telemetry volume? Sampling can be configured to reduce volume while maintaining statistical accuracy.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: ALL application components (frontend, backend, storage layer) MUST emit telemetry to Azure Application Insights
- **FR-002**: System MUST use ONLY the `azure-monitor-opentelemetry` package for telemetry collection to ensure compatibility with Azure Monitor health model and Azure Service Groups
- **FR-003**: Backend MUST report cloud role name as "azure-service-catalog-backend" via `OTEL_SERVICE_NAME` environment variable
- **FR-004**: Frontend MUST report cloud role name as "azure-service-catalog-frontend" via `OTEL_SERVICE_NAME` environment variable
- **FR-005**: System MUST automatically instrument HTTP requests, responses, and exceptions
- **FR-006**: System MUST propagate trace context between frontend and backend for distributed tracing
- **FR-007**: Storage operations MUST be instrumented with custom spans including operation type and duration
- **FR-008**: System MUST gracefully degrade when Application Insights is unavailable (no crashes, log warning)
- **FR-009**: System MUST use environment variables for configuration (no hardcoded connection strings)
- **FR-010**: OpenCensus packages MUST be removed from all dependencies (incompatible with Azure Monitor health model)

### Key Entities

- **Trace**: Represents a complete request flow across services, identified by a trace ID
- **Span**: Represents a single operation within a trace (e.g., HTTP request, storage call)
- **Cloud Role**: Identifies a service component in the Application Map (frontend, backend)

## Technical Constraints *(mandatory)*

### Mandatory SDK Requirement

> **CRITICAL**: The **Azure Monitor OpenTelemetry Python SDK** (`azure-monitor-opentelemetry` package) is the ONLY permitted telemetry library for this project. This requirement ensures compatibility with:
> - **Azure Monitor health model** for unified health signals
> - **Azure Service Groups** for resource health aggregation
> - **Application Map** for distributed tracing visualization
> 
> OpenCensus and other telemetry libraries are PROHIBITED as they are incompatible with Azure Monitor's health model integration.

### All Components Must Emit Telemetry

Every application component MUST emit telemetry to Azure Application Insights:

| Component | Cloud Role Name | Telemetry Types |
|-----------|----------------|-----------------|
| Frontend (Streamlit) | `azure-service-catalog-frontend` | Logs, HTTP client spans, exceptions |
| Backend (FastAPI) | `azure-service-catalog-backend` | Logs, HTTP server spans, exceptions, custom spans |
| Storage Layer | (child of backend) | Custom spans for storage operations |

### Must Use

- **azure-monitor-opentelemetry** PyPI package (the official Azure Monitor OpenTelemetry Distro)
- **OpenTelemetry semantic conventions** for resource attributes (`service.name`, `service.namespace`, `service.instance.id`)
- **Environment variables** for configuration (`OTEL_SERVICE_NAME`, `OTEL_RESOURCE_ATTRIBUTES`, `APPLICATIONINSIGHTS_CONNECTION_STRING`)
- **configure_azure_monitor()** function as the single entry point for telemetry configuration

### Must Avoid

- **OpenCensus** packages (`opencensus-ext-azure`, `opencensus.trace`) - deprecated and incompatible with Azure Monitor health model
- Hardcoded connection strings in code
- Custom telemetry initializers when environment variables suffice
- Alternative telemetry SDKs (e.g., raw OpenTelemetry exporters without Azure Monitor distro)

### Performance Requirements

- Telemetry collection must not add more than 5ms latency to API requests
- Use async-compatible instrumentation where possible
- Use 100% sampling ratio (`sampling_ratio=1.0`) for all environments to capture every request
- Enable Live Metrics (`enable_live_metrics=True`) for real-time operational monitoring

### Compatibility Requirements

- Python 3.11+
- FastAPI 0.109+
- Streamlit 1.30+
- Azure App Service Linux (Python 3.11)

## Out of Scope *(mandatory)*

The following items are explicitly excluded from this feature:

1. **Browser/client-side telemetry** - JavaScript instrumentation for browser metrics (would require separate implementation)
2. **Custom metrics and dashboards** - Creating Azure Monitor Workbooks or custom dashboards (can be done later)
3. **Alerts and action groups** - Setting up alerting rules on telemetry (operational concern, not code change)
4. **Profiler and Snapshot Debugger** - Advanced debugging features (not available for Python)
5. **Log Analytics queries** - Writing KQL queries for analysis (separate operational task)
6. **Multi-region failover** - Telemetry routing to multiple Application Insights instances

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All API requests appear in Application Insights Transaction Search within 5 minutes of execution
- **SC-002**: Application Map shows two distinct nodes (frontend, backend) with correct cloud role names
- **SC-003**: End-to-end traces show complete request flow from frontend through backend to storage
- **SC-004**: Exceptions are captured with full stack traces in the Failures view
- **SC-005**: Storage operations appear as child spans with operation name and duration
- **SC-006**: Zero OpenCensus dependencies remain in the codebase after implementation

## Questions & Assumptions *(mandatory)*

## Clarifications

### Session 2026-01-12

- Q: Should we enable Live Metrics for real-time monitoring? → A: Yes, enable Live Metrics (`enable_live_metrics=True`)
- Q: What sampling ratio should be used in production? → A: 100% sampling - capture every request

### Resolved Questions

1. **Q**: Should we enable Live Metrics for real-time monitoring?  
   **Status**: ✅ Resolved  
   **Decision**: Enable Live Metrics with `enable_live_metrics=True` for real-time operational monitoring

2. **Q**: What sampling ratio should be used in production?  
   **Status**: ✅ Resolved  
   **Decision**: Use 100% sampling (`sampling_ratio=1.0`) to capture every request

### Assumptions

1. **A**: The existing `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable is already configured in Azure App Service through Terraform.  
   **Validated by**: Reading terraform outputs shows `application_insights_connection_string` is set

2. **A**: The current OpenCensus implementation can be fully replaced without breaking changes - it only provides logging, not custom business metrics.  
   **Validated by**: Code review shows OpenCensus is only used for log export and basic tracing

3. **A**: Both frontend and backend share the same Application Insights resource but need distinct cloud role names.  
   **Validated by**: Terraform configuration shows single Application Insights resource for the entire application

## Dependencies

### External Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| azure-monitor-opentelemetry | PyPI Package | Azure Monitor OpenTelemetry Distro for Python |
| opentelemetry-instrumentation-fastapi | PyPI Package | Automatic FastAPI instrumentation (included in distro) |
| opentelemetry-instrumentation-httpx | PyPI Package | HTTP client instrumentation for API calls |

### Internal Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| Application Insights resource | Azure Resource | Already provisioned via Terraform |
| Environment variables | Configuration | APPLICATIONINSIGHTS_CONNECTION_STRING already set |

## Implementation Approach

### Phase 1: Backend Telemetry (P1)

1. Remove OpenCensus dependencies from `backend/pyproject.toml`
2. Add `azure-monitor-opentelemetry` dependency
3. Create `src/telemetry.py` module with `configure_telemetry()` function
4. Call `configure_azure_monitor()` at application startup with `OTEL_SERVICE_NAME=azure-service-catalog-backend`
5. Update logging to use the configured logger namespace
6. Update Terraform to add `OTEL_SERVICE_NAME` environment variable

### Phase 2: Frontend Telemetry (P2)

1. Remove OpenCensus dependencies from `frontend/pyproject.toml`
2. Add `azure-monitor-opentelemetry` dependency
3. Create `src/telemetry.py` module for frontend
4. Configure with `OTEL_SERVICE_NAME=azure-service-catalog-frontend`
5. Update Terraform to add `OTEL_SERVICE_NAME` environment variable

### Phase 3: Storage Instrumentation (P3)

1. Add OpenTelemetry spans to storage adapter methods
2. Use `tracer.start_as_current_span()` for manual instrumentation of key operations
3. Include storage operation type and service name as span attributes

## References

- [Enable Azure Monitor OpenTelemetry](https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-enable?tabs=python)
- [Configure Azure Monitor OpenTelemetry](https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-configuration?tabs=python)
- [Set Cloud Role Name](https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-configuration?tabs=python#set-the-cloud-role-name-and-the-cloud-role-instance)
- [OpenTelemetry Python SDK](https://opentelemetry.io/docs/languages/python/)
- [Azure Monitor OpenTelemetry Distro GitHub](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry)
