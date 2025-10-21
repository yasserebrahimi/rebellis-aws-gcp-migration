# 🔐 Security Architecture

- **Zero‑trust**: service‑to‑service auth (mTLS or JWT)
- **Least privilege**: Workload Identity + minimal IAM
- **Image security**: SBOM, Trivy, Binary Authorization
- **Network**: Default‑deny NetworkPolicies; Cloud Armor WAF
- **Secrets**: GSM + External Secrets; no plaintext in Git
- **Data**: At‑rest and in‑transit encryption (TLS 1.3)
