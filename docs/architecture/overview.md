# 🏗️ Architecture Overview

Rebellis converts text into motion in near‑real time. The backend orchestrates model serving (NVIDIA Triton) and streams results to clients via REST/WebSocket. It is optimized for low latency, resilience, and cost efficiency on GKE Autopilot.

**Key principles**
- Separation of concerns for API, inference, and stream processing
- Horizontal scalability and GPU pool isolation
- Observability baked in (RED/USE, SLOs, golden signals)
- Security by default (least privilege, zero‑trust, signed images)
- Immutable infrastructure; declarative config (Helm/Terraform)

```mermaid
flowchart LR
  A[Clients\nUnity/Web] -->|REST/WebSocket| B(API FastAPI)
  B -->|/v1/infer| E[Whisper GPU Service]
  B -->|/v1/animate| F[Motion GPU Service]
  E -. gRPC .-> T[Triton Inference Server]
  F -. gRPC .-> T
  B --> R[(Redis Queue)]
  B --> D[(Cloud SQL: Postgres)]
  subgraph GKE
    B:::svc; E:::svc; F:::svc; T:::svc
    subgraph Obs[Observability]
      P[Prometheus] --> G[Grafana]
      L[Loki] --> G
      Alerter[Alertmanager] --> OnCall[Slack/PagerDuty]
    end
  end
  classDef svc fill:#eef,stroke:#55f,stroke-width:1px;
```
