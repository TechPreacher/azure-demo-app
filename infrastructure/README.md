# Infrastructure Deployment Guide

This directory contains Terraform configurations for deploying the Azure Service Catalog to Azure.

## Prerequisites

Before deploying, ensure you have:

1. **Azure Account** with an active subscription
2. **Azure CLI** installed and authenticated
3. **Terraform** >= 1.0.0 installed

### Install Prerequisites

```bash
# Install Azure CLI (macOS)
brew install azure-cli

# Install Terraform (macOS)
brew install terraform

# Or use tfenv for version management
brew install tfenv
tfenv install 1.6.0
tfenv use 1.6.0
```

### Authenticate with Azure

```bash
# Login to Azure
az login

# Verify subscription
az account show

# Set subscription (if you have multiple)
az account set --subscription "<subscription-id>"
```

## Architecture

The Terraform configuration deploys:

```
┌─────────────────────────────────────────────────────────────┐
│                    Resource Group                           │
│  ┌───────────────┐  ┌───────────────┐  ┌────────────────┐  │
│  │  App Service  │  │    Storage    │  │  Application   │  │
│  │     Plan      │  │    Account    │  │   Insights     │  │
│  │               │  │               │  │                │  │
│  │  ┌─────────┐  │  │  ┌─────────┐  │  │  ┌──────────┐  │  │
│  │  │ Backend │  │  │  │  Blob   │  │  │  │   Log    │  │  │
│  │  │  (API)  │  │  │  │Container│  │  │  │Analytics │  │  │
│  │  └─────────┘  │  │  └─────────┘  │  │  │Workspace │  │  │
│  │  ┌─────────┐  │  │               │  │  └──────────┘  │  │
│  │  │Frontend │  │  │               │  │                │  │
│  │  │  (UI)   │  │  │               │  │                │  │
│  │  └─────────┘  │  │               │  │                │  │
│  └───────────────┘  └───────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Resources Created

| Resource | Purpose |
|----------|---------|
| Resource Group | Container for all resources |
| App Service Plan | Hosts both App Services (Linux, Python 3.11) |
| Backend App Service | FastAPI backend API |
| Frontend App Service | Streamlit web UI |
| Storage Account | Blob storage for services.json |
| Blob Container | Contains the services data file |
| Application Insights | Monitoring and telemetry (optional) |
| Log Analytics Workspace | Log storage for Application Insights |

## Deployment

### Step 1: Configure Variables

```bash
# Copy the example variables file
cp terraform.tfvars.example terraform.tfvars

# Edit with your settings
vim terraform.tfvars
```

Key variables to configure:

| Variable | Description | Example |
|----------|-------------|---------|
| `project_name` | Prefix for all resources (3-12 chars) | `azsvccat` |
| `environment` | Environment name | `dev`, `staging`, `prod` |
| `location` | Azure region | `eastus`, `westus2` |

### Step 2: Initialize Terraform

```bash
cd infrastructure
terraform init
```

This downloads the required providers and initializes the backend.

### Step 3: Plan Deployment

```bash
# Review what will be created
terraform plan

# Or with specific variables
terraform plan -var="environment=staging" -var="location=westus2"
```

### Step 4: Apply Configuration

```bash
# Deploy to Azure
terraform apply

# Auto-approve (use with caution)
terraform apply -auto-approve
```

### Step 5: Verify Deployment

After successful deployment, Terraform outputs important information:

```bash
# View all outputs
terraform output

# Get specific values
terraform output frontend_app_url
terraform output backend_app_url
terraform output -raw storage_connection_string
```

Test the deployment:

```bash
# Check backend health
curl $(terraform output -raw backend_app_url)/health

# Open frontend in browser
open $(terraform output -raw frontend_app_url)
```

## Deploy Application Code

After infrastructure is deployed, deploy your application code:

### Option A: ZIP Deploy

```bash
# Backend
cd ../backend
zip -r ../backend.zip . -x "*.pyc" -x "__pycache__/*" -x ".venv/*"
az webapp deploy --resource-group $(terraform output -raw resource_group_name) \
  --name $(terraform output -raw backend_app_name) \
  --src-path ../backend.zip --type zip

# Frontend
cd ../frontend
zip -r ../frontend.zip . -x "*.pyc" -x "__pycache__/*" -x ".venv/*"
az webapp deploy --resource-group $(terraform output -raw resource_group_name) \
  --name $(terraform output -raw frontend_app_name) \
  --src-path ../frontend.zip --type zip
```

### Option B: Git Deployment

Configure deployment source in Azure Portal or via CLI:

```bash
# Enable local Git deployment
az webapp deployment source config-local-git \
  --resource-group $(terraform output -raw resource_group_name) \
  --name $(terraform output -raw backend_app_name)
```

## Environment-Specific Deployments

### Development

```bash
terraform workspace new dev || terraform workspace select dev
terraform apply -var-file="environments/dev.tfvars"
```

### Staging

```bash
terraform workspace new staging || terraform workspace select staging
terraform apply -var-file="environments/staging.tfvars"
```

### Production

```bash
terraform workspace new prod || terraform workspace select prod
terraform apply -var-file="environments/prod.tfvars"
```

## Tear Down

To destroy all resources:

```bash
# Review what will be destroyed
terraform plan -destroy

# Destroy resources
terraform destroy
```

⚠️ **Warning**: This will permanently delete all data in blob storage.

## Remote State (Production)

For team collaboration, configure remote state storage:

1. Create a storage account for Terraform state:

```bash
# Create resource group for state
az group create --name tfstate-rg --location eastus

# Create storage account
az storage account create \
  --name tfstatesa$(date +%s | tail -c 6) \
  --resource-group tfstate-rg \
  --sku Standard_LRS

# Create container
az storage container create \
  --name tfstate \
  --account-name <storage-account-name>
```

2. Uncomment and configure the backend in `providers.tf`:

```hcl
backend "azurerm" {
  resource_group_name  = "tfstate-rg"
  storage_account_name = "<storage-account-name>"
  container_name       = "tfstate"
  key                  = "azure-service-catalog.tfstate"
}
```

3. Re-initialize Terraform:

```bash
terraform init -migrate-state
```

## Troubleshooting

### Common Issues

**Error: Storage account name already exists**

Storage account names must be globally unique. The configuration includes a random suffix, but if you get this error, try:

```bash
terraform taint random_string.suffix
terraform apply
```

**Error: App Service startup failed**

Check the application logs:

```bash
az webapp log tail \
  --resource-group $(terraform output -raw resource_group_name) \
  --name $(terraform output -raw backend_app_name)
```

**Error: CORS issues**

The backend CORS is configured to allow the frontend URL. If you're testing from a different origin, add it to the `cors.allowed_origins` in the App Service module.

### Useful Commands

```bash
# View resource group resources
az resource list --resource-group $(terraform output -raw resource_group_name) -o table

# Restart App Services
az webapp restart --resource-group $(terraform output -raw resource_group_name) \
  --name $(terraform output -raw backend_app_name)

# View App Service configuration
az webapp config show --resource-group $(terraform output -raw resource_group_name) \
  --name $(terraform output -raw backend_app_name)

# Stream logs
az webapp log tail --resource-group $(terraform output -raw resource_group_name) \
  --name $(terraform output -raw backend_app_name)
```

## Cost Estimation

Approximate monthly costs (Basic B1 tier, East US):

| Resource | Estimated Cost |
|----------|---------------|
| App Service Plan (B1) | ~$13/month |
| Storage Account (LRS) | ~$1/month |
| Application Insights | ~$2-5/month |
| **Total** | **~$16-20/month** |

For development, consider using the Free tier (F1) for App Service Plan.

## Security Considerations

1. **Connection Strings**: Stored as App Settings, consider using Key Vault for production
2. **Network Security**: Consider adding VNet integration for production
3. **Authentication**: Add Azure AD authentication for production workloads
4. **TLS**: Enforced via `min_tls_version = "TLS1_2"` on storage account
5. **Public Access**: Blob container is private, only accessible via connection string
