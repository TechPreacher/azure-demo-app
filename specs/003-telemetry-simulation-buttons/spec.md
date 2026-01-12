# Feature Specification: Telemetry Simulation Buttons

**Feature Branch**: `003-telemetry-simulation-buttons`  
**Created**: 2026-01-12  
**Status**: Draft  
**Input**: Add two buttons to the frontend that simulate telemetry scenarios: a "Latency" button that triggers a slow response (10-20 seconds random delay), and an "Error" button that triggers a 500 server error with realistic error messages.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Simulate High Latency Response (Priority: P1)

As a developer/operator, I want a "Latency" button in the frontend that triggers a slow backend response (10-20 seconds), so that I can test how the application handles latency and verify that Application Insights captures slow dependency calls.

**Why this priority**: Latency simulation is essential for testing timeout handling, user experience during slow operations, and verifying that Application Insights properly captures duration metrics and slow transaction traces.

**Independent Test**: Can be tested by clicking the "Latency" button and observing: (1) the UI shows a loading state, (2) the response arrives after 10-20 seconds, and (3) Application Insights shows a trace with the corresponding duration.

**Acceptance Scenarios**:

1. **Given** the frontend is loaded, **When** a user clicks the "Latency" button, **Then** a loading indicator is displayed while waiting for the response.
2. **Given** the "Latency" button is clicked, **When** the backend receives the request, **Then** it waits for a random duration between 10 and 20 seconds before responding.
3. **Given** the latency simulation completes, **When** viewing Application Insights traces, **Then** the request shows a duration matching the simulated delay.
4. **Given** the latency endpoint is called, **When** the response is returned, **Then** it includes the actual delay time in the response body for verification.

---

### User Story 2 - Simulate Server Error Response (Priority: P1)

As a developer/operator, I want an "Error" button in the frontend that triggers a 500 Internal Server Error with realistic error messages, so that I can test error handling, verify Application Insights captures exceptions, and validate the Failures view in Azure Monitor.

**Why this priority**: Error simulation is critical for testing exception handling, error boundaries, user-facing error messages, and verifying that Application Insights properly captures and categorizes exceptions.

**Independent Test**: Can be tested by clicking the "Error" button and observing: (1) the UI displays an appropriate error message, (2) the backend returns HTTP 500, and (3) Application Insights Failures view shows the exception.

**Acceptance Scenarios**:

1. **Given** the frontend is loaded, **When** a user clicks the "Error" button, **Then** an error notification is displayed to the user.
2. **Given** the "Error" button is clicked, **When** the backend receives the request, **Then** it returns HTTP 500 with a realistic, varying error message.
3. **Given** the error endpoint is called, **When** viewing Application Insights Failures, **Then** the exception is logged with stack trace and error details.
4. **Given** the error endpoint is called multiple times, **When** checking the error messages, **Then** each call returns a different realistic error message to simulate real-world varying failures.

---

### Edge Cases

- What happens when the latency button is clicked multiple times rapidly? Each request should be handled independently with its own random delay.
- What happens when the latency request times out on the client side? The frontend should handle timeouts gracefully with a user-friendly message.
- What happens when the error simulation endpoint itself fails unexpectedly? The endpoint should still return a proper HTTP 500 response.

## Requirements *(mandatory)*

### Functional Requirements

**Backend Endpoints**:

- **FR-001**: Backend MUST expose a `POST /api/v1/simulate/latency` endpoint that introduces a random delay between 10 and 20 seconds before responding.
- **FR-002**: The latency endpoint response MUST include the actual delay duration in the response body (e.g., `{"status": "completed", "delay_seconds": 15.3}`).
- **FR-003**: Backend MUST expose a `POST /api/v1/simulate/error` endpoint that returns HTTP 500 Internal Server Error.
- **FR-004**: The error endpoint MUST return varying, realistic error messages from a predefined list (e.g., "Database connection pool exhausted", "Memory allocation failed", "Upstream service timeout").
- **FR-005**: The error endpoint MUST include a unique error ID in the response for correlation in Application Insights.
- **FR-006**: Both simulation endpoints MUST be properly instrumented with OpenTelemetry for tracing.

**Frontend UI**:

- **FR-007**: Frontend MUST display a "Latency" button in the sidebar or main UI area.
- **FR-008**: Frontend MUST display an "Error" button in the sidebar or main UI area.
- **FR-009**: Clicking "Latency" button MUST show a loading/spinner state with text indicating the simulation is running.
- **FR-010**: Clicking "Error" button MUST display the error message returned by the backend in a user-friendly format.
- **FR-011**: Both buttons MUST be visually distinct and clearly labeled as simulation/testing tools.
- **FR-012**: The latency button timeout MUST be configured to at least 30 seconds to accommodate the maximum simulated delay.

### Non-Functional Requirements

- **NFR-001**: Simulation endpoints SHALL remain enabled in all environments including production (simplicity over security isolation for this demo application).
- **NFR-002**: Error messages MUST be realistic but MUST NOT expose actual system information or secrets.
- **NFR-003**: Latency simulation MUST NOT block other backend operations (use async sleep).

### Key Entities

- **SimulationResponse**: Response model for simulation endpoints containing status, details, and correlation ID.
- **ErrorMessage**: Predefined list of realistic error messages for random selection.

## Technical Constraints *(mandatory)*

### Backend Implementation

The simulation endpoints follow the existing FastAPI router pattern:

```python
# Example structure (not actual implementation)
@router.post("/simulate/latency")
async def simulate_latency():
    delay = random.uniform(10.0, 20.0)
    await asyncio.sleep(delay)
    return {"status": "completed", "delay_seconds": round(delay, 2)}

@router.post("/simulate/error")
async def simulate_error():
    error_messages = [
        "Database connection pool exhausted",
        "Memory allocation failed during request processing",
        "Upstream service timed out after 30 seconds",
        # ... more messages
    ]
    error_id = str(uuid.uuid4())
    raise HTTPException(
        status_code=500,
        detail={"message": random.choice(error_messages), "error_id": error_id}
    )
```

### Frontend Implementation

The buttons integrate with the existing Streamlit UI in the sidebar:

```python
# Example structure (not actual implementation)
st.sidebar.header("🧪 Telemetry Simulation")
if st.sidebar.button("⏱️ Simulate Latency", help="Triggers a 10-20 second delay"):
    with st.spinner("Simulating latency..."):
        result = client.simulate_latency()
        st.success(f"Completed in {result['delay_seconds']} seconds")

if st.sidebar.button("❌ Simulate Error", help="Triggers a 500 server error"):
    try:
        client.simulate_error()
    except APIError as e:
        st.error(f"Simulated error: {e}")
```

### API Client Extension

The API client needs new methods:

```python
def simulate_latency(self, timeout: float = 30.0) -> dict:
    """Trigger latency simulation endpoint."""
    ...

def simulate_error(self) -> None:
    """Trigger error simulation endpoint (will raise APIError)."""
    ...
```

## API Contract *(mandatory)*

### POST /api/v1/simulate/latency

**Description**: Simulates a slow backend response with random delay.

**Request**: No body required.

**Response** (200 OK):
```json
{
  "status": "completed",
  "delay_seconds": 15.32,
  "message": "Latency simulation completed successfully"
}
```

**Telemetry**: Creates a trace span "simulate_latency" with duration attribute.

---

### POST /api/v1/simulate/error

**Description**: Simulates a 500 Internal Server Error with realistic messages.

**Request**: No body required.

**Response** (500 Internal Server Error):
```json
{
  "detail": {
    "message": "Database connection pool exhausted after 10 retries",
    "error_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2026-01-12T10:30:00Z"
  }
}
```

**Error Messages Pool** (randomly selected):
- "Database connection pool exhausted after 10 retries"
- "Memory allocation failed during request processing"
- "Upstream service 'inventory-api' timed out after 30 seconds"
- "Disk I/O error: Unable to write to temporary storage"
- "SSL certificate validation failed for external dependency"
- "Request payload exceeded maximum allowed size"
- "Rate limit exceeded: Too many requests from client"
- "Cache invalidation cascade triggered system protection"

**Telemetry**: Creates an exception record with full stack trace in Application Insights Failures.

## Success Metrics

- Both buttons are visible and functional in the frontend UI
- Latency simulation consistently produces delays in the 10-20 second range
- Error simulation returns HTTP 500 with varying error messages
- All simulations appear correctly in Application Insights (traces and failures)
- No impact on existing application functionality

## Out of Scope

- Configurable delay ranges (fixed 10-20 seconds for this iteration)
- Custom error messages via UI input
- Simulation scheduling or automation
- Production environment deployment of simulation endpoints

## Dependencies

- Spec 002: Azure Monitor OpenTelemetry Integration (required for telemetry visibility)
- Existing FastAPI backend infrastructure
- Existing Streamlit frontend infrastructure

## Clarifications

### Session 2026-01-12

- Q: Should simulation endpoints be disabled in production environments? → A: No, keep enabled everywhere (simpler implementation)
