# Azure Services Backend

FastAPI backend for the Azure Service Catalog application.

## Development

```bash
# Install dependencies
uv sync --all-extras

# Run development server
uv run uvicorn src.main:app --reload --port 8000

# Run tests
uv run pytest
```

## API Endpoints

- `GET /health` - Health check
- `GET /api/v1/services` - List services
- `GET /api/v1/services/{name}` - Get service by name
- `POST /api/v1/services` - Create service
- `PUT /api/v1/services/{name}` - Update service
- `DELETE /api/v1/services/{name}` - Delete service

## Telemetry Configuration

The backend uses Azure Monitor OpenTelemetry SDK for observability.

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | Application Insights connection string | Yes (for telemetry) |
| `OTEL_SERVICE_NAME` | Cloud role name (default: `azure-service-catalog-backend`) | No |

### Features

- **Automatic Instrumentation**: FastAPI HTTP requests are automatically traced
- **Live Metrics**: Real-time performance monitoring in Azure Portal
- **Storage Spans**: Custom spans for storage operations (list, get, create, update, delete)
- **Graceful Degradation**: Application runs without telemetry if connection string is not set

### Local Development

```bash
# Copy .env.example and configure
cp .env.example .env
# Edit .env with your Application Insights connection string

# Run with telemetry
uv run uvicorn src.main:app --reload
```

### Viewing Telemetry

1. Open Azure Portal → Application Insights resource
2. **Application Map**: Shows backend node with cloud role name
3. **Transaction Search**: View HTTP traces with storage spans
4. **Live Metrics**: Real-time request rates and latency
5. **Failures**: View exceptions with stack traces
