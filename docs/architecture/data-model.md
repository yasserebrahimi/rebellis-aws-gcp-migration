# 🗄️ Data Model

```mermaid
erDiagram
  USER ||--o{ SESSION : has
  PROJECT ||--o{ JOB : has
  JOB ||--o{ ARTIFACT : produces

  USER {{
    uuid id
    string email
    string name
    datetime created_at
  }}

  PROJECT {{
    uuid id
    uuid owner_id
    string name
    jsonb config
    datetime created_at
  }}

  JOB {{
    uuid id
    uuid project_id
    enum status  // queued|running|succeeded|failed
    float input_duration_s
    float gpu_seconds
    datetime created_at
    datetime completed_at
  }}

  ARTIFACT {{
    uuid id
    uuid job_id
    string type   // transcript|motion|preview
    string uri    // gcs://bucket/key
    jsonb meta
    datetime created_at
  }}
```
**Migrations**: managed via Alembic; see `deployment/terraform.md` for Cloud SQL provisioning.
