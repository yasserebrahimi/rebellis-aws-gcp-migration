# 🌐 Topology & Networking

- **Ingress**: Cloud Load Balancer → Cloud Armor (WAF) → Ingress (Istio/NGINX)
- **Service Mesh (optional)**: Mutual TLS, retries, timeouts
- **Pods**: anti‑affinity; resource requests/limits; GPU node pools tainted
- **Data Layer**: Cloud SQL (HA), Redis Memorystore, GCS for artifacts
- **Egress**: Cloud NAT with restricted egress; Private Service Connect
