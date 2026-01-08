# Terraform Outputs
# Exposes important values for use in deployment and configuration

# -----------------------------------------------------------------------------
# Resource Group
# -----------------------------------------------------------------------------

output "resource_group_name" {
  description = "Name of the resource group containing all resources"
  value       = module.resource_group.name
}

output "resource_group_location" {
  description = "Azure region where resources are deployed"
  value       = module.resource_group.location
}

# -----------------------------------------------------------------------------
# Storage Account
# -----------------------------------------------------------------------------

output "storage_account_name" {
  description = "Name of the Azure Storage Account"
  value       = module.storage.storage_account_name
}

output "storage_blob_endpoint" {
  description = "Primary blob endpoint URL"
  value       = module.storage.primary_blob_endpoint
}

output "storage_container_name" {
  description = "Name of the blob container for services.json"
  value       = module.storage.container_name
}

output "storage_connection_string" {
  description = "Connection string for the storage account (sensitive)"
  value       = module.storage.primary_connection_string
  sensitive   = true
}

# -----------------------------------------------------------------------------
# App Services
# -----------------------------------------------------------------------------

output "backend_app_name" {
  description = "Name of the backend App Service"
  value       = module.app_service.backend_app_name
}

output "backend_app_url" {
  description = "URL to access the backend API"
  value       = module.app_service.backend_app_url
}

output "frontend_app_name" {
  description = "Name of the frontend App Service"
  value       = module.app_service.frontend_app_name
}

output "frontend_app_url" {
  description = "URL to access the frontend application"
  value       = module.app_service.frontend_app_url
}

# -----------------------------------------------------------------------------
# Monitoring (if enabled)
# -----------------------------------------------------------------------------

output "application_insights_name" {
  description = "Name of the Application Insights instance"
  value       = var.enable_monitoring ? module.monitoring[0].application_insights_name : null
}

output "application_insights_connection_string" {
  description = "Connection string for Application Insights (sensitive)"
  value       = var.enable_monitoring ? module.monitoring[0].connection_string : null
  sensitive   = true
}

output "application_insights_instrumentation_key" {
  description = "Instrumentation key for Application Insights (sensitive)"
  value       = var.enable_monitoring ? module.monitoring[0].instrumentation_key : null
  sensitive   = true
}

# -----------------------------------------------------------------------------
# Summary Output (for easy reference)
# -----------------------------------------------------------------------------

output "deployment_summary" {
  description = "Summary of deployed resources and URLs"
  value = {
    environment    = var.environment
    resource_group = module.resource_group.name
    frontend_url   = module.app_service.frontend_app_url
    backend_url    = module.app_service.backend_app_url
    health_check   = "${module.app_service.backend_app_url}/health"
  }
}
