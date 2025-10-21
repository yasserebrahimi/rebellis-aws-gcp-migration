# 🧱 Terraform Infrastructure

Modules:
- `networking`: VPC, subnets, NAT
- `gke`: Autopilot cluster, GPU node pools (T4/L4)
- `cloudsql`: PostgreSQL HA, private IP
- `memorystore`: Redis
- `artifacts`: Artifact Registry
- `monitoring`: Alert policies, dashboards

## Usage
```bash
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```
**Outputs**: cluster endpoint, DB connection, service accounts, Redis URI.
