# Project Structure


rebellis-aws-gcp-migration/
â”œâ”€â”€ terraform/gcp/
â”‚   â”œâ”€â”€ main.tf
â”‚   â”œâ”€â”€ variables.tf
â”‚   â”œâ”€â”€ gke_cluster.tf
â”‚   â”œâ”€â”€ vpc_network.tf
â”‚   â””â”€â”€ cloud_sql.tf
â”œâ”€â”€ kubernetes/base/
â”‚   â””â”€â”€ backend-api/
â”‚       â””â”€â”€ deployment.yaml
â”œâ”€â”€ scripts/migration/
â”‚   â””â”€â”€ 01-setup-gcp-project.sh
â”œâ”€â”€ docs/
â”œâ”€â”€ .github/workflows/
â”œâ”€â”€ README.md
â””â”€â”€ .gitignore

**Total Files**: 11
**Total Lines of Code**: ~450
