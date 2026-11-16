# Terraform configuration

This folder contains a safe, locally validatable Terraform example for the NexusOps Lite platform. It is intentionally lightweight and does not require AWS credentials or paid infrastructure.

The configuration documents the project name and environment, which represent the local deployment metadata that a real infrastructure definition would use.

## Validate locally

```powershell
cd C:\Users\baijunath karvir\Desktop\Nexus_Ops\NexusOps-Lite\ninfrastructure\terraform
terraform fmt
terraform validate
```

This configuration is intentionally non-destructive and does not call `terraform apply`.
