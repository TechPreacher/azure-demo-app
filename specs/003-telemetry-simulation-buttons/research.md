# Research: Telemetry Simulation Buttons

**Feature**: 003-telemetry-simulation-buttons  
**Date**: 2026-01-12  
**Status**: Complete

## Research Tasks

### 1. FastAPI Async Sleep for Latency Simulation

**Question**: How to implement non-blocking delay in FastAPI endpoint?

**Decision**: Use `asyncio.sleep()` with async endpoint handler

**Rationale**: 
- FastAPI is built on Starlette/ASGI which fully supports async operations
- `asyncio.sleep()` yields control to event loop, allowing other requests to be processed
- Native Python stdlib, no additional dependencies required

**Alternatives Considered**:
- `time.sleep()` - REJECTED: Blocks the entire worker thread, degrading performance
- Background task with polling - REJECTED: Over-engineering for simple delay simulation
- External delay service - REJECTED: Adds unnecessary complexity and network latency

**Implementation Pattern**:
```python
import asyncio
import random

@router.post("/simulate/latency")
async def simulate_latency():
    delay = random.uniform(10.0, 20.0)
    await asyncio.sleep(delay)  # Non-blocking
    return {"delay_seconds": round(delay, 2)}
```

---

### 2. HTTPException for Error Simulation

**Question**: How to return structured 500 errors in FastAPI with custom detail?

**Decision**: Raise `HTTPException` with `status_code=500` and dict `detail`

**Rationale**:
- FastAPI's `HTTPException` automatically handles JSON serialization
- Custom `detail` dict allows structured error responses
- Automatic OpenTelemetry exception capture with proper stack traces
- Consistent with existing error handling patterns in the codebase

**Alternatives Considered**:
- Custom exception class - REJECTED: Unnecessary for simulation; adds complexity
- Return Response with 500 status - REJECTED: Doesn't trigger exception telemetry
- Starlette HTTPException - REJECTED: FastAPI's version preferred for better OpenAPI integration

**Implementation Pattern**:
```python
from fastapi import HTTPException
import uuid

@router.post("/simulate/error")
async def simulate_error():
    error_id = str(uuid.uuid4())
    raise HTTPException(
        status_code=500,
        detail={"message": "...", "error_id": error_id}
    )
```

---

### 3. Streamlit Button with Long-Running Operation

**Question**: How to handle 10-20 second button operations in Streamlit without timeout?

**Decision**: Use `st.spinner()` context manager with extended httpx timeout

**Rationale**:
- `st.spinner()` provides visual feedback during long operations
- httpx client supports per-request timeout configuration
- Streamlit handles the async wait internally

**Alternatives Considered**:
- Background thread with polling - REJECTED: Complicates state management
- WebSocket for progress updates - REJECTED: Over-engineering for simulation
- Async Streamlit (experimental) - REJECTED: Not stable enough for production

**Implementation Pattern**:
```python
if st.button("Simulate Latency"):
    with st.spinner("Simulating latency (10-20 seconds)..."):
        result = client.simulate_latency(timeout=30.0)
        st.success(f"Completed in {result['delay_seconds']}s")
```

---

### 4. OpenTelemetry Span Attributes for Simulation

**Question**: How to add custom attributes to OpenTelemetry spans for simulation tracking?

**Decision**: Use automatic FastAPI instrumentation; spans created automatically

**Rationale**:
- `azure-monitor-opentelemetry` automatically instruments FastAPI
- HTTP duration captured in span duration field
- Exception details automatically captured for 500 errors
- No custom span creation needed for basic simulation

**Alternatives Considered**:
- Manual span creation with `tracer.start_as_current_span()` - REJECTED: Unnecessary overhead
- Custom span attributes for delay value - DEFERRED: Can add later if needed for filtering

**Reference**: Azure Monitor OpenTelemetry auto-instrumentation captures:
- HTTP method, route, status code
- Request/response duration
- Exception type, message, stack trace (for errors)

---

### 5. Realistic Error Message Pool

**Question**: What error messages simulate realistic production failures?

**Decision**: Curated list of 8 common infrastructure/application errors

**Rationale**:
- Messages should be recognizable as "real" errors
- Variety ensures logs show different failure types
- No actual system information exposed (security)

**Error Message Pool**:
| Category | Message |
|----------|---------|
| Database | "Database connection pool exhausted after 10 retries" |
| Memory | "Memory allocation failed during request processing" |
| Upstream | "Upstream service 'inventory-api' timed out after 30 seconds" |
| I/O | "Disk I/O error: Unable to write to temporary storage" |
| SSL | "SSL certificate validation failed for external dependency" |
| Payload | "Request payload exceeded maximum allowed size" |
| Rate Limit | "Rate limit exceeded: Too many requests from client" |
| Cache | "Cache invalidation cascade triggered system protection" |

---

### 6. API Client Timeout Configuration

**Question**: How to configure extended timeout for latency endpoint in httpx?

**Decision**: Use `timeout` parameter on individual request

**Rationale**:
- httpx supports per-request timeout override
- Default client timeout (30s) sufficient for error endpoint
- Only latency endpoint needs extended timeout

**Implementation Pattern**:
```python
def simulate_latency(self) -> dict:
    response = self._client.post(
        self._get_url("simulate/latency"),
        timeout=30.0  # Override default for this request
    )
    return self._handle_response(response)
```

---

## Summary

All technical questions resolved. No NEEDS CLARIFICATION items remain.

| Topic | Decision | Confidence |
|-------|----------|------------|
| Async delay | `asyncio.sleep()` | High |
| Error response | `HTTPException` with dict detail | High |
| UI feedback | `st.spinner()` with extended timeout | High |
| Telemetry | Auto-instrumentation sufficient | High |
| Error messages | 8-message curated pool | High |
| Client timeout | Per-request override | High |
