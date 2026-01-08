# App Service Module
# Creates App Service Plan and two App Services (backend and frontend)

variable "name" {
  description = "Base name for App Service resources"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region for App Service resources"
  type        = string
}

variable "sku_tier" {
  description = "SKU tier for the App Service Plan"
  type        = string
  default     = "Basic"
}

variable "sku_size" {
  description = "SKU size for the App Service Plan"
  type        = string
  default     = "B1"
}

variable "backend_app_settings" {
  description = "App settings for the backend App Service"
  type        = map(string)
  default     = {}
}

variable "frontend_app_settings" {
  description = "App settings for the frontend App Service"
  type        = map(string)
  default     = {}
}

variable "storage_account_name" {
  description = "Name of the Azure Storage Account"
  type        = string
}

variable "storage_account_id" {
  description = "ID of the Azure Storage Account for role assignment"
  type        = string
}

variable "storage_container_name" {
  description = "Name of the blob container for services.json"
  type        = string
}

variable "application_insights_connection_string" {
  description = "Connection string for Application Insights"
  type        = string
  sensitive   = true
  default     = ""
}

variable "application_insights_instrumentation_key" {
  description = "Instrumentation key for Application Insights"
  type        = string
  sensitive   = true
  default     = ""
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

# App Service Plan (Linux)
resource "azurerm_service_plan" "this" {
  name                = "${var.name}-plan"
  location            = var.location
  resource_group_name = var.resource_group_name
  os_type             = "Linux"
  sku_name            = var.sku_size

  tags = var.tags
}

# Backend App Service (FastAPI)
resource "azurerm_linux_web_app" "backend" {
  name                = "${var.name}-backend"
  location            = var.location
  resource_group_name = var.resource_group_name
  service_plan_id     = azurerm_service_plan.this.id

  # Enable system-assigned managed identity
  identity {
    type = "SystemAssigned"
  }

  site_config {
    application_stack {
      python_version = "3.11"
    }

    always_on        = var.sku_tier != "Free" && var.sku_tier != "Shared"
    app_command_line = "uvicorn src.main:app --host 0.0.0.0 --port 8000"

    cors {
      allowed_origins = [
        "https://${var.name}-frontend.azurewebsites.net",
        "http://localhost:8501"
      ]
    }
  }

  app_settings = merge(
    {
      # Storage configuration (using managed identity)
      "STORAGE_TYPE"                = "azure"
      "AZURE_STORAGE_ACCOUNT_NAME"  = var.storage_account_name
      "AZURE_BLOB_CONTAINER_NAME"   = var.storage_container_name
      "AZURE_STORAGE_USE_MANAGED_IDENTITY" = "true"

      # Application Insights
      "APPLICATIONINSIGHTS_CONNECTION_STRING" = var.application_insights_connection_string
      "APPINSIGHTS_INSTRUMENTATIONKEY"        = var.application_insights_instrumentation_key

      # Python configuration
      "SCM_DO_BUILD_DURING_DEPLOYMENT" = "true"
      "WEBSITES_PORT"                  = "8000"
    },
    var.backend_app_settings
  )

  tags = var.tags
}

# Role assignment: Backend App Service -> Storage Blob Data Contributor
resource "azurerm_role_assignment" "backend_storage" {
  scope                = var.storage_account_id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_linux_web_app.backend.identity[0].principal_id
}

# Frontend App Service (Streamlit)
resource "azurerm_linux_web_app" "frontend" {
  name                = "${var.name}-frontend"
  location            = var.location
  resource_group_name = var.resource_group_name
  service_plan_id     = azurerm_service_plan.this.id

  site_config {
    application_stack {
      python_version = "3.11"
    }

    always_on        = var.sku_tier != "Free" && var.sku_tier != "Shared"
    app_command_line = "streamlit run src/app.py --server.port 8501 --server.address 0.0.0.0"
  }

  app_settings = merge(
    {
      # Backend API URL
      "API_BASE_URL" = "https://${azurerm_linux_web_app.backend.default_hostname}"

      # Application Insights
      "APPLICATIONINSIGHTS_CONNECTION_STRING" = var.application_insights_connection_string
      "APPINSIGHTS_INSTRUMENTATIONKEY"        = var.application_insights_instrumentation_key

      # Python/Streamlit configuration
      "SCM_DO_BUILD_DURING_DEPLOYMENT" = "true"
      "WEBSITES_PORT"                  = "8501"
    },
    var.frontend_app_settings
  )

  tags = var.tags
}

output "app_service_plan_id" {
  description = "ID of the App Service Plan"
  value       = azurerm_service_plan.this.id
}

output "backend_app_name" {
  description = "Name of the backend App Service"
  value       = azurerm_linux_web_app.backend.name
}

output "backend_app_url" {
  description = "Default URL of the backend App Service"
  value       = "https://${azurerm_linux_web_app.backend.default_hostname}"
}

output "backend_app_id" {
  description = "ID of the backend App Service"
  value       = azurerm_linux_web_app.backend.id
}

output "frontend_app_name" {
  description = "Name of the frontend App Service"
  value       = azurerm_linux_web_app.frontend.name
}

output "frontend_app_url" {
  description = "Default URL of the frontend App Service"
  value       = "https://${azurerm_linux_web_app.frontend.default_hostname}"
}

output "frontend_app_id" {
  description = "ID of the frontend App Service"
  value       = azurerm_linux_web_app.frontend.id
}
