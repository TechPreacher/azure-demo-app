# Azure Service Catalog

A demo CRUD application for managing Azure service definitions, built with FastAPI (backend), Streamlit (frontend), and deployed to Azure using Terraform.

## Features

- **View** all Azure services in a searchable table
- **Create** new Azure service entries
- **Update** existing service information
- **Delete** services from the catalog
- **Filter** services by name or category

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.11+, FastAPI, Pydantic |
| Frontend | Python 3.11+, Streamlit |
| Storage | Azure Blob Storage (prod) / Local JSON (dev) |
| Infrastructure | Terraform, Azure App Service |

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) - Python package manager
- [Terraform](https://www.terraform.io/) (for Azure deployment)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/) (for Azure deployment)

## Quick Start (Local Development)

### 1. Clone and setup

```bash
git clone <repository-url>
cd azure-demo-app
```

### 2. Install dependencies

```bash
# Backend
cd backend
uv sync --all-extras
cd ..

# Frontend
cd frontend
uv sync --all-extras
cd ..
```

### 3. Run the application

**Option A: Using the dev script**

```bash
./scripts/dev.sh
```

**Option B: Manual startup**

```bash
# Terminal 1: Backend (port 8000)
cd backend
uv run uvicorn src.main:app --reload --port 8000

# Terminal 2: Frontend (port 8501)
cd frontend
uv run streamlit run src/app.py --server.port 8501
```

### 4. Access the application

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Project Structure

```
azure-demo-app/
├── backend/                 # FastAPI backend service
│   ├── src/
│   │   ├── api/            # API routes and dependencies
│   │   ├── models/         # Pydantic models
│   │   ├── services/       # Business logic (storage adapters)
│   │   ├── config.py       # Configuration
│   │   └── main.py         # FastAPI app entry point
│   ├── tests/              # Backend tests
│   └── pyproject.toml
├── frontend/               # Streamlit frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── api_client.py   # Backend API client
│   │   ├── config.py       # Configuration
│   │   └── app.py          # Streamlit main app
│   ├── tests/              # Frontend tests
│   └── pyproject.toml
├── infrastructure/         # Terraform IaC
│   ├── modules/            # Terraform modules
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── data/
│   └── services.json       # Default seed data
├── scripts/
│   ├── dev.sh             # Local development script
│   └── test.sh            # Run all tests
└── README.md
```

## Running Tests

```bash
# Run all tests
./scripts/test.sh

# Backend tests only
cd backend && uv run pytest

# Frontend tests only
cd frontend && uv run pytest

# With coverage report
cd backend && uv run pytest --cov=src --cov-report=html
```

## Environment Variables

### Backend

| Variable | Description | Default |
|----------|-------------|---------|
| `STORAGE_TYPE` | Storage adapter: `local` or `azure` | `local` |
| `AZURE_STORAGE_CONNECTION_STRING` | Azure Blob Storage connection string | - |
| `AZURE_STORAGE_CONTAINER_NAME` | Blob container name | `services` |
| `LOCAL_DATA_PATH` | Path to local services.json | `../data/services.json` |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | App Insights connection | - |

### Frontend

| Variable | Description | Default |
|----------|-------------|---------|
| `API_BASE_URL` | Backend API URL | `http://localhost:8000` |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | App Insights connection | - |

## Azure Deployment

See [infrastructure/README.md](infrastructure/README.md) for detailed deployment instructions.

### Prerequisites

- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/) authenticated (`az login`)
- [Terraform](https://www.terraform.io/) >= 1.0.0

### Quick Deploy

```bash
cd infrastructure

# Configure variables (edit as needed)
cp terraform.tfvars.example terraform.tfvars

# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Apply (creates all Azure resources)
terraform apply
```

### Post-Deployment

After Terraform completes:

```bash
# Get deployment URLs
terraform output deployment_summary

# Test backend health
curl $(terraform output -raw backend_app_url)/health

# Open frontend
open $(terraform output -raw frontend_app_url)
```

### Deployed Resources

| Resource | Description |
|----------|-------------|
| Resource Group | Contains all project resources |
| App Service Plan | Linux plan hosting both services |
| Backend App Service | FastAPI API (Python 3.11) |
| Frontend App Service | Streamlit UI (Python 3.11) |
| Storage Account | Blob storage for services.json |
| Application Insights | Monitoring and telemetry |

### Tear Down

```bash
terraform destroy
```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/services` | List all services |
| GET | `/api/v1/services/{name}` | Get service by name |
| POST | `/api/v1/services` | Create new service |
| PUT | `/api/v1/services/{name}` | Update service |
| DELETE | `/api/v1/services/{name}` | Delete service |

## License

MIT
