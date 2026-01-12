#!/usr/bin/env bash
# Deploy script for Azure Service Catalog
# Deploys backend and frontend to Azure App Service

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
INFRA_DIR="$PROJECT_ROOT/infrastructure"

echo "🚀 Azure Service Catalog Deployment"
echo "===================================="

# Check for required tools
check_tool() {
    if ! command -v "$1" &> /dev/null; then
        echo "❌ $1 is not installed. Please install it first."
        exit 1
    fi
}

check_tool az
check_tool zip

# Check Azure CLI login
echo "🔐 Checking Azure CLI authentication..."
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure CLI. Please run 'az login' first."
    exit 1
fi

# Get deployment values from Terraform state
echo "📋 Reading deployment configuration from Terraform state..."
cd "$INFRA_DIR"

RESOURCE_GROUP=$(terraform output -raw resource_group_name 2>/dev/null)
BACKEND_APP=$(terraform output -raw backend_app_name 2>/dev/null)
FRONTEND_APP=$(terraform output -raw frontend_app_name 2>/dev/null)
STORAGE_ACCOUNT=$(terraform output -raw storage_account_name 2>/dev/null)
STORAGE_CONTAINER=$(terraform output -raw storage_container_name 2>/dev/null)

if [ -z "$RESOURCE_GROUP" ] || [ -z "$BACKEND_APP" ] || [ -z "$FRONTEND_APP" ]; then
    echo "❌ Could not read Terraform outputs. Make sure infrastructure is deployed."
    echo "   Run 'cd infrastructure && terraform apply' first."
    exit 1
fi

echo ""
echo "📦 Deployment Configuration:"
echo "   Resource Group:    $RESOURCE_GROUP"
echo "   Backend App:       $BACKEND_APP"
echo "   Frontend App:      $FRONTEND_APP"
echo "   Storage Account:   $STORAGE_ACCOUNT"
echo "   Storage Container: $STORAGE_CONTAINER"
echo ""

# Upload services.json to blob storage
echo "📤 Uploading services.json to Azure Blob Storage..."
az storage blob upload \
    --account-name "$STORAGE_ACCOUNT" \
    --container-name "$STORAGE_CONTAINER" \
    --name "services.json" \
    --file "$PROJECT_ROOT/data/services.json" \
    --overwrite \
    --auth-mode login

echo "✅ services.json uploaded successfully"

# Deploy Backend
echo ""
echo "🔧 Deploying Backend to $BACKEND_APP..."
cd "$PROJECT_ROOT/backend"

# Create requirements.txt from pyproject.toml dependencies
echo "   Creating requirements.txt..."
cat > requirements.txt << 'EOF'
fastapi>=0.109.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
uvicorn[standard]>=0.27.0
azure-storage-blob>=12.19.0
azure-identity>=1.15.0
azure-monitor-opentelemetry>=1.0.0
httpx>=0.26.0
EOF

# Create deployment package
echo "   Creating deployment package..."
rm -f backend.zip
zip -r backend.zip src requirements.txt -x "*.pyc" -x "*__pycache__*" -x "*.pytest_cache*"

# Deploy to App Service
echo "   Deploying to Azure App Service..."
az webapp deploy \
    --resource-group "$RESOURCE_GROUP" \
    --name "$BACKEND_APP" \
    --src-path backend.zip \
    --type zip \
    --async true

# Clean up
rm -f requirements.txt backend.zip

echo "✅ Backend deployment initiated"

# Deploy Frontend
echo ""
echo "🎨 Deploying Frontend to $FRONTEND_APP..."
cd "$PROJECT_ROOT/frontend"

# Create requirements.txt from pyproject.toml dependencies
echo "   Creating requirements.txt..."
cat > requirements.txt << 'EOF'
streamlit>=1.30.0
httpx>=0.26.0
azure-monitor-opentelemetry>=1.0.0
EOF

# Create deployment package
echo "   Creating deployment package..."
rm -f frontend.zip
zip -r frontend.zip src startup.sh requirements.txt -x "*.pyc" -x "*__pycache__*" -x "*.pytest_cache*"

# Deploy to App Service
echo "   Deploying to Azure App Service..."
az webapp deploy \
    --resource-group "$RESOURCE_GROUP" \
    --name "$FRONTEND_APP" \
    --src-path frontend.zip \
    --type zip \
    --async true

# Clean up
rm -f requirements.txt frontend.zip

echo "✅ Frontend deployment initiated"

# Get URLs
BACKEND_URL=$(terraform -chdir="$INFRA_DIR" output -raw backend_app_url 2>/dev/null)
FRONTEND_URL=$(terraform -chdir="$INFRA_DIR" output -raw frontend_app_url 2>/dev/null)

echo ""
echo "===================================="
echo "🎉 Deployment Complete!"
echo ""
echo "   Frontend:  $FRONTEND_URL"
echo "   Backend:   $BACKEND_URL"
echo "   API Docs:  $BACKEND_URL/docs"
echo ""
echo "⏳ Note: Deployments are async. It may take 1-2 minutes for apps to be ready."
echo "   Check deployment status with:"
echo "   az webapp log tail -g $RESOURCE_GROUP -n $BACKEND_APP"
echo "   az webapp log tail -g $RESOURCE_GROUP -n $FRONTEND_APP"
