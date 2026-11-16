terraform {
  required_version = ">= 1.5.0"
}

variable "project_name" {
  description = "Name of the deployment project"
  type        = string
  default     = "nexusops-lite"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

locals {
  deployment_label = "${var.project_name}-${var.environment}"
}

output "deployment_label" {
  description = "The deployment label that would be used for local platform configuration"
  value       = local.deployment_label
}

output "summary" {
  description = "Terraform summary for this demonstration infrastructure"
  value       = "This configuration demonstrates the local infrastructure footprint required for ${local.deployment_label}."
}
