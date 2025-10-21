# 📚 Rebellis Documentation Hub (English)

Production-ready documentation for **Rebellis — Real‑Time Text‑to‑Motion AI Backend**.

- Stack: **FastAPI**, **Python**, **NVIDIA Triton/TensorRT**, **PostgreSQL**, **Redis**, **GKE Autopilot**, **Helm**, **KEDA**, **Prometheus/Grafana**, **Loki**, **Cloud SQL**, **Cloud Armor**.
- CI/CD: **GitHub Actions**, **GCR/Artifact Registry**, progressive delivery with canary.

**Last updated:** 2025-10-21

## Contents
| Area | Description |
|------|-------------|
| [Quick Start](quickstart.md) | Install, run locally, deploy to staging/prod |
| [Architecture Overview](architecture/overview.md) | High-level system view |
| [Service Catalog](architecture/services.md) | Responsibilities & contracts |
| [Topology](architecture/topology.md) | Networking & components layout |
| [Data Model](architecture/data-model.md) | ERD, storage, migrations |
| [Sequence Diagrams](architecture/sequence-diagrams.md) | Critical request flows |
| [API Reference](api/openapi.yaml) | OpenAPI 3.1 spec |
| [Configuration](configs/env-vars.md) | Environment variables & defaults |
| [Deployment (Helm)](deployment/helm.md) | Commands & values |
| [Infrastructure (Terraform)](deployment/terraform.md) | IaC modules & usage |
| [Autoscaling](deployment/autoscaling.md) | KEDA/HPA triggers |
| [Secrets Management](deployment/secrets.md) | External Secrets & SM |
| [Observability](monitoring/observability.md) | Prometheus/Grafana/Loki |
| [SLOs](monitoring/slo.md) | Targets & measurement |
| [Alerting](monitoring/alerting.md) | Policies & escalation |
| [Security Architecture](security/security.md) | Zero‑trust & boundaries |
| [RBAC](security/rbac.md) | Roles & scopes |
| [Policies](security/policies.md) | Kyverno/OPA |
| [Threat Model](security/threat-model.md) | STRIDE table & mitigations |
| [Compliance](security/compliance.md) | Data retention & privacy |
| [CI/CD Pipelines](ci-cd/pipelines.md) | Workflow details |
| [Releases & Versioning](ci-cd/releasing.md) | SemVer & change control |
| [Branching Strategy](ci-cd/branching.md) | Git conventions |
| [Testing Strategy](testing/strategy.md) | Unit/integration/e2e |
| [API Tests](testing/api-tests.md) | pytest/httpx examples |
| [Load & Perf](testing/load-testing.md) | k6 scenarios |
| [Chaos](testing/chaos-testing.md) | Fault injection |
| [Performance Tuning](performance/tuning.md) | GPU/CPU/DB tuning |
| [Capacity Planning](performance/capacity-planning.md) | Sizing worksheets |
| [Operations Runbooks](operations/README.md) | On‑call guides |
| [Troubleshooting](troubleshooting/common.md) | Frequent issues |
| [FAQ](troubleshooting/faq.md) | Common questions |
| [Migration AWS→GCP](migration/aws-to-gcp.md) | Cutover plan |
| [Cutover Checklist](migration/cutover-checklist.md) | Pre/post steps |
| [Glossary](glossary.md) | Domain & infra terms |
| [Diagrams (Mermaid)](diagrams/) | Sources for diagrams |

---
© 2025 Rebellis
