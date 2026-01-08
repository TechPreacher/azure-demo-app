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
