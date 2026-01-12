# Azure Services Frontend

Streamlit frontend for the Azure Service Catalog application.

## Development

```bash
# Install dependencies
uv sync --all-extras

# Run development server
uv run streamlit run src/app.py --server.port 8501

# Run tests
uv run pytest
```

## Configuration

Set `API_BASE_URL` environment variable to point to the backend API.
Default: `http://localhost:8000`

## Telemetry Configuration

The frontend uses Azure Monitor OpenTelemetry SDK for observability.

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | Application Insights connection string | Yes (for telemetry) |
| `OTEL_SERVICE_NAME` | Cloud role name (default: `azure-service-catalog-frontend`) | No |

### Features

- **Automatic Instrumentation**: HTTP client requests are automatically traced
- **Live Metrics**: Real-time performance monitoring in Azure Portal
- **Distributed Tracing**: Traces connect frontend to backend requests
- **Graceful Degradation**: Application runs without telemetry if connection string is not set

### Local Development

```bash
# Copy .env.example and configure
cp .env.example .env
# Edit .env with your Application Insights connection string

# Run with telemetry
uv run streamlit run src/app.py
```

### Viewing Telemetry

1. Open Azure Portal → Application Insights resource
2. **Application Map**: Shows frontend and backend nodes with connections
3. **Transaction Search**: View end-to-end traces from frontend through backend
4. **Live Metrics**: Real-time request rates and latency
5. **Failures**: View exceptions with stack traces
