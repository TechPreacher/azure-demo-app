# Quickstart: Telemetry Simulation Buttons

**Feature**: 003-telemetry-simulation-buttons  
**Date**: 2026-01-12

## Overview

This guide covers implementing the telemetry simulation buttons feature, which adds two frontend buttons that trigger backend endpoints for testing Application Insights telemetry capture.

## Prerequisites

- Python 3.11+
- Backend and frontend services from spec 001
- Azure Monitor OpenTelemetry integration from spec 002
- Application Insights connection string configured

## Implementation Steps

### Step 1: Create Backend Simulation Router

Create `backend/src/api/simulation.py`:

```python
"""Simulation endpoints for telemetry testing."""

import asyncio
import logging
import random
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/simulate", tags=["Simulation"])

# Error message pool for realistic failures
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


class LatencySimulationResponse(BaseModel):
    """Response model for latency simulation."""
    status: str = Field(default="completed")
    delay_seconds: float = Field(ge=10.0, le=20.0)
    message: str = Field(default="Latency simulation completed successfully")


@router.post("/latency", response_model=LatencySimulationResponse)
async def simulate_latency() -> LatencySimulationResponse:
    """Simulate high latency (10-20 seconds)."""
    delay = random.uniform(10.0, 20.0)
    logger.info(f"Starting latency simulation: {delay:.2f} seconds")
    
    await asyncio.sleep(delay)
    
    logger.info(f"Latency simulation completed: {delay:.2f} seconds")
    return LatencySimulationResponse(delay_seconds=round(delay, 2))


@router.post("/error")
async def simulate_error() -> None:
    """Simulate 500 Internal Server Error."""
    error_id = str(uuid.uuid4())
    message = random.choice(ERROR_MESSAGES)
    timestamp = datetime.now(timezone.utc).isoformat()
    
    logger.error(f"Simulating error: {message} (error_id={error_id})")
    
    raise HTTPException(
        status_code=500,
        detail={
            "message": message,
            "error_id": error_id,
            "timestamp": timestamp,
        },
    )
```

### Step 2: Register Router in Main App

Update `backend/src/main.py` to include the simulation router:

```python
from src.api.simulation import router as simulation_router

# After existing router registration
app.include_router(simulation_router)
```

### Step 3: Add API Client Methods

Add to `frontend/src/api_client.py`:

```python
def simulate_latency(self) -> dict[str, Any]:
    """Trigger latency simulation endpoint.
    
    Returns:
        Response with delay_seconds and status.
    
    Raises:
        APIError: If request fails or times out.
    """
    try:
        response = self._client.post(
            self._get_url("simulate/latency"),
            timeout=30.0,  # Extended timeout for 10-20s delay
        )
        return self._handle_response(response)
    except httpx.TimeoutException as e:
        raise APIError("Latency simulation timed out") from e

def simulate_error(self) -> None:
    """Trigger error simulation endpoint.
    
    Raises:
        APIError: Always raises with simulated error details.
    """
    response = self._client.post(self._get_url("simulate/error"))
    # This will raise APIError due to 500 status
    self._handle_response(response)
```

### Step 4: Add Simulation Buttons to Frontend

Add to `frontend/src/app.py` (in sidebar section):

```python
# Telemetry Simulation Section
st.sidebar.divider()
st.sidebar.header("🧪 Telemetry Simulation")
st.sidebar.caption("Test Application Insights integration")

col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("⏱️ Latency", help="Triggers 10-20 second delay"):
        with st.spinner("Simulating latency..."):
            try:
                client = get_api_client()
                result = client.simulate_latency()
                st.success(f"✅ {result['delay_seconds']}s")
            except APIError as e:
                st.error(f"Failed: {e}")

with col2:
    if st.button("❌ Error", help="Triggers 500 server error"):
        try:
            client = get_api_client()
            client.simulate_error()
        except APIError as e:
            st.error(f"Simulated: {e}")
```

## Testing

### Manual Testing

1. Start backend: `cd backend && uvicorn src.main:app --reload`
2. Start frontend: `cd frontend && streamlit run src/app.py`
3. Click "Latency" button - observe 10-20 second wait
4. Click "Error" button - observe error message display
5. Check Application Insights:
   - Transaction Search for latency traces
   - Failures view for simulated errors

### Automated Tests

Run from repository root:

```bash
# Unit tests
cd backend && pytest tests/unit/test_simulation.py -v

# Integration tests  
cd backend && pytest tests/integration/test_simulation_api.py -v
```

## Verification Checklist

- [ ] Latency button shows spinner during wait
- [ ] Latency response displays actual delay time
- [ ] Error button displays error message
- [ ] Error messages vary between clicks
- [ ] Traces appear in Application Insights within 5 minutes
- [ ] Exceptions appear in Failures view
- [ ] No impact on existing CRUD functionality
