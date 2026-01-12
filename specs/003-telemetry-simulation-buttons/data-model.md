# Data Model: Telemetry Simulation Buttons

**Feature**: 003-telemetry-simulation-buttons  
**Date**: 2026-01-12

## Overview

This feature introduces minimal data models for simulation endpoint responses. No persistent storage or database entities are required.

## Entities

### LatencySimulationResponse

Response model for the latency simulation endpoint.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | string | Yes | Operation status, always "completed" on success |
| `delay_seconds` | float | Yes | Actual delay applied in seconds (10.0-20.0 range) |
| `message` | string | Yes | Human-readable completion message |

**Pydantic Model**:
```python
from pydantic import BaseModel, Field

class LatencySimulationResponse(BaseModel):
    """Response from latency simulation endpoint."""
    status: str = Field(default="completed", description="Operation status")
    delay_seconds: float = Field(ge=10.0, le=20.0, description="Applied delay in seconds")
    message: str = Field(default="Latency simulation completed successfully")
```

**Example**:
```json
{
  "status": "completed",
  "delay_seconds": 15.32,
  "message": "Latency simulation completed successfully"
}
```

---

### ErrorSimulationDetail

Error detail structure for the error simulation endpoint (embedded in HTTPException).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | Yes | Randomly selected error message from pool |
| `error_id` | string (UUID) | Yes | Unique identifier for correlation |
| `timestamp` | string (ISO 8601) | Yes | Time when error was generated |

**Note**: This is not a Pydantic response model; it's the `detail` dict passed to `HTTPException`.

**Example**:
```json
{
  "message": "Database connection pool exhausted after 10 retries",
  "error_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-01-12T10:30:00Z"
}
```

---

### ErrorMessagePool

Static collection of realistic error messages for random selection.

| Index | Message | Category |
|-------|---------|----------|
| 0 | "Database connection pool exhausted after 10 retries" | Database |
| 1 | "Memory allocation failed during request processing" | Memory |
| 2 | "Upstream service 'inventory-api' timed out after 30 seconds" | Upstream |
| 3 | "Disk I/O error: Unable to write to temporary storage" | I/O |
| 4 | "SSL certificate validation failed for external dependency" | SSL |
| 5 | "Request payload exceeded maximum allowed size" | Payload |
| 6 | "Rate limit exceeded: Too many requests from client" | Rate Limit |
| 7 | "Cache invalidation cascade triggered system protection" | Cache |

**Implementation**:
```python
ERROR_MESSAGES: list[str] = [
    "Database connection pool exhausted after 10 retries",
    "Memory allocation failed during request processing",
    "Upstream service 'inventory-api' timed out after 30 seconds",
    "Disk I/O error: Unable to write to temporary storage",
    "SSL certificate validation failed for external dependency",
    "Request payload exceeded maximum allowed size",
    "Rate limit exceeded: Too many requests from client",
    "Cache invalidation cascade triggered system protection",
]
```

---

## Relationships

```text
┌─────────────────────────┐
│   Frontend (Streamlit)  │
│  ┌───────────────────┐  │
│  │ Latency Button    │──┼─── POST /api/v1/simulate/latency ───►
│  └───────────────────┘  │                                      │
│  ┌───────────────────┐  │                                      │
│  │ Error Button      │──┼─── POST /api/v1/simulate/error ──────►
│  └───────────────────┘  │                                      │
└─────────────────────────┘                                      │
                                                                 │
┌─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────┐
│   Backend (FastAPI)     │
│  ┌───────────────────┐  │
│  │ /simulate/latency │──┼───► LatencySimulationResponse
│  │ (async sleep)     │  │
│  └───────────────────┘  │
│  ┌───────────────────┐  │
│  │ /simulate/error   │──┼───► HTTPException(500, ErrorSimulationDetail)
│  │ (raise exception) │  │
│  └───────────────────┘  │
└─────────────────────────┘
           │
           ▼
┌─────────────────────────┐
│  Application Insights   │
│  - Traces (latency)     │
│  - Failures (errors)    │
└─────────────────────────┘
```

## Validation Rules

### LatencySimulationResponse
- `delay_seconds` MUST be between 10.0 and 20.0 (inclusive)
- `status` MUST be "completed" for successful responses

### ErrorSimulationDetail
- `error_id` MUST be a valid UUID v4 format
- `message` MUST be selected from `ERROR_MESSAGES` pool
- `timestamp` MUST be valid ISO 8601 format

## State Transitions

N/A - Simulation endpoints are stateless; no state transitions apply.
