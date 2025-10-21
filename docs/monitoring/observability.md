# 👁️ Observability

- **Prometheus**: scrape `/metrics` from all services
- **Grafana**: pre‑built dashboards (API, GPU, Infra, Cost)
- **Loki**: structured JSON logging; correlation IDs
- **Alertmanager**: paging via Slack/PagerDuty

**Metrics**
- RED (Rate, Errors, Duration) for API
- GPU: utilization, memory, batch size, queue depth
- DB: connections, slow queries, cache hit ratio
