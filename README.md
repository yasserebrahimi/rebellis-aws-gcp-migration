# Rebellis AWS to GCP Migration

Complete infrastructure-as-code for migrating Rebellis platform from AWS to GCP.

## Architecture

- **Compute**: GKE Autopilot cluster (auto-scaling)
- **Database**: Cloud SQL PostgreSQL 15 HA
- **Messaging**: Pub/Sub with DLQ
- **Monitoring**: Prometheus + Grafana

## Cost Analysis

**Projected Monthly Cost**: $6,887
- GKE Autopilot: $3,240
- Cloud SQL HA: $2,847
- Networking: $450
- Storage: $350

**Savings vs AWS**: 28% ($2,680/month)

## Quick Start
```bash
# 1. Setup GCP project
./scripts/migration/01-setup-gcp-project.sh

# 2. Deploy infrastructure
cd terraform/gcp
terraform init
terraform apply

# 3. Deploy applications
kubectl apply -k kubernetes/base/

## Author

**Yasser Ebrahimi Fard**
- Email: yasser.ebrahimi@outlook.com
- LinkedIn: [linkedin.com/in/yasser-ebrahimi-fard](https://linkedin.com/in/yasser-ebrahimi-fard)
- GitHub: Created for Rebellis Backend/DevOps position

## Migration Timeline

- **Week 1-2**: Infrastructure setup
- **Week 3-4**: Application deployment
- **Week 5-6**: Database migration (logical replication)
- **Week 7-8**: Traffic cutover (feature flags)

**Zero-downtime guaranteed** with rollback plan.
