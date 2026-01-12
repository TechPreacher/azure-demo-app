# Quickstart: Azure Monitor OpenTelemetry Integration

**Feature**: 002-azure-otel-telemetry  
**Date**: 2026-01-12

## Prerequisites

- Python 3.11+
- Azure subscription with Application Insights resource (already provisioned via Terraform)
- Access to Application Insights connection string

## Local Development Setup

### 1. Install Dependencies

After implementation, sync dependencies in both projects:

```bash
# Backend
cd backend
uv sync

# Frontend
cd ../frontend
uv sync
```

### 2. Configure Environment Variables

Create or update `.env` files:

**backend/.env**:
```bash
# Storage (existing)
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=../data/services.json

# Telemetry (new)
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=xxx;...
OTEL_SERVICE_NAME=azure-service-catalog-backend
```

**frontend/.env**:
```bash
# API (existing)
API_BASE_URL=http://localhost:8000

# Telemetry (new)
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=xxx;...
OTEL_SERVICE_NAME=azure-service-catalog-frontend
```

> **Note**: For local development without App Insights, omit `APPLICATIONINSIGHTS_CONNECTION_STRING`. The application will log a warning and run without telemetry.

### 3. Run Services

```bash
# From repository root
./scripts/dev.sh
```

### 4. Verify Telemetry

1. Make API requests (e.g., visit `http://localhost:8501`)
2. Open Azure Portal → Application Insights resource
3. Navigate to **Transaction Search** → filter by last 30 minutes
4. Verify traces appear with correct cloud role names

## Key Files After Implementation

```text
backend/
├── src/
│   ├── telemetry.py          # Telemetry configuration
│   └── main.py               # Imports telemetry first
└── pyproject.toml            # azure-monitor-opentelemetry dependency

frontend/
├── src/
│   ├── telemetry.py          # Telemetry configuration
│   └── app.py                # Imports telemetry first
└── pyproject.toml            # azure-monitor-opentelemetry dependency
```

## Telemetry Module Pattern

Both backend and frontend use the same pattern:

```python
# src/telemetry.py
import logging
import os

logger = logging.getLogger(__name__)

def configure_telemetry() -> None:
    """Configure Azure Monitor OpenTelemetry.
    
    Must be called before importing application modules (FastAPI/Streamlit).
    Gracefully degrades if connection string is not set.
    """
    connection_string = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    
    if not connection_string:
        logger.warning(
            "APPLICATIONINSIGHTS_CONNECTION_STRING not set - telemetry disabled"
        )
        return
    
    from azure.monitor.opentelemetry import configure_azure_monitor
    
    configure_azure_monitor(
        enable_live_metrics=True,
        sampling_ratio=1.0,
    )
    logger.info("Azure Monitor telemetry configured")
```

## Azure Deployment

Environment variables are configured via Terraform:

```hcl
# infrastructure/modules/app_service/main.tf

app_settings = {
  # Backend
  "OTEL_SERVICE_NAME" = "azure-service-catalog-backend"
  "APPLICATIONINSIGHTS_CONNECTION_STRING" = var.application_insights_connection_string
  
  # Frontend
  "OTEL_SERVICE_NAME" = "azure-service-catalog-frontend"
  "APPLICATIONINSIGHTS_CONNECTION_STRING" = var.application_insights_connection_string
}
```

After Terraform apply, deploy application code:

```bash
./scripts/deploy.sh
```

## Viewing Telemetry in Azure Portal

### Application Map

1. Azure Portal → Application Insights → Application Map
2. Two nodes visible:
   - `azure-service-catalog-frontend`
   - `azure-service-catalog-backend`
3. Connection lines show request flow

### Transaction Search

1. Azure Portal → Application Insights → Transaction Search
2. Filter by:
   - Time range: Last 30 minutes
   - Event types: Request, Dependency, Exception
3. Click any request to see end-to-end trace

### Live Metrics

1. Azure Portal → Application Insights → Live Metrics
2. Real-time view of:
   - Request rate
   - Response time
   - Failure rate
3. Useful for monitoring deployments

### Failures

1. Azure Portal → Application Insights → Failures
2. View exceptions with:
   - Full stack traces
   - Request context
   - Affected users

## Troubleshooting

### Telemetry Not Appearing

1. Verify environment variables are set:
   ```bash
   echo $APPLICATIONINSIGHTS_CONNECTION_STRING
   echo $OTEL_SERVICE_NAME
   ```

2. Check application logs for telemetry configuration message:
   ```
   INFO - Azure Monitor telemetry configured
   ```

3. Wait 2-5 minutes—telemetry has ingestion delay

### Duplicate Cloud Role Names

If Application Map shows unexpected nodes:

1. Verify each service has unique `OTEL_SERVICE_NAME`
2. Restart both services after changing environment variables

### High Telemetry Volume

Sampling is set to 100% by design. If volume is too high:

1. Reduce `sampling_ratio` in `configure_azure_monitor()` call
2. Update both frontend and backend consistently

## Testing Telemetry

Run unit tests to verify telemetry module:

```bash
# Backend
cd backend
uv run pytest tests/unit/test_telemetry.py -v

# Frontend
cd ../frontend
uv run pytest tests/test_telemetry.py -v
```
