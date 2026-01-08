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
