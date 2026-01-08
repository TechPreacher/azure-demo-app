# Resource Group Module
# Creates an Azure Resource Group to contain all project resources

variable "name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region for the resource group"
  type        = string
}

variable "tags" {
  description = "Tags to apply to the resource group"
  type        = map(string)
  default     = {}
}

resource "azurerm_resource_group" "this" {
  name     = var.name
  location = var.location
  tags     = var.tags
}

output "name" {
  description = "Name of the created resource group"
  value       = azurerm_resource_group.this.name
}

output "id" {
  description = "ID of the created resource group"
  value       = azurerm_resource_group.this.id
}

output "location" {
  description = "Location of the created resource group"
  value       = azurerm_resource_group.this.location
}
