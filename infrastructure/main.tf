# Main Terraform Configuration
# Composes all modules to create the Azure Service Catalog infrastructure

# Local values for naming conventions
locals {
  # Resource naming: {project}-{environment}-{resource}
  name_prefix = "${var.project_name}-${var.environment}"

  # Storage account names must be globally unique and 3-24 lowercase alphanumeric
  storage_account_name = "${var.project_name}${var.environment}sa"

  # Common tags applied to all resources
  common_tags = merge(
    {
      Project     = "Azure Service Catalog"
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.tags
  )
}

# Generate a random suffix for globally unique names
resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

# Resource Group
module "resource_group" {
  source = "./modules/resource_group"

  name     = "${local.name_prefix}-rg"
  location = var.location
  tags     = local.common_tags
}

# Storage Account for services.json
module "storage" {
  source = "./modules/storage"

  name                = "${local.storage_account_name}${random_string.suffix.result}"
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  account_tier        = var.storage_account_tier
  replication_type    = var.storage_account_replication
  container_name      = var.blob_container_name
  tags                = local.common_tags
}

# Application Insights (conditional)
module "monitoring" {
  source = "./modules/monitoring"
  count  = var.enable_monitoring ? 1 : 0

  name                = local.name_prefix
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  retention_days      = var.log_retention_days
  tags                = local.common_tags
}

# App Services (Backend + Frontend)
module "app_service" {
  source = "./modules/app_service"

  name                = local.name_prefix
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  sku_tier            = var.app_service_sku.tier
  sku_size            = var.app_service_sku.size

  # Storage configuration (using managed identity)
  storage_account_name   = module.storage.storage_account_name
  storage_account_id     = module.storage.storage_account_id
  storage_container_name = module.storage.container_name

  # Application Insights configuration (if enabled)
  application_insights_connection_string   = var.enable_monitoring ? module.monitoring[0].connection_string : ""
  application_insights_instrumentation_key = var.enable_monitoring ? module.monitoring[0].instrumentation_key : ""

  # Additional app settings
  backend_app_settings  = var.backend_app_settings
  frontend_app_settings = var.frontend_app_settings

  tags = local.common_tags
}
