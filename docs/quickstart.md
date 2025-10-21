# 🚀 Quick Start

## Local Development
```bash
git clone <your-repo-url>
cd <repo>
cp .env.example .env
docker compose up -d
open http://localhost:8000/docs  # FastAPI Swagger UI
pytest -q --maxfail=1 --disable-warnings --cov
```

## Required Environment Variables
```
APP_ENV=local|staging|production
GCP_PROJECT_ID=your-project
GCP_REGION=us-central1
CLUSTER_NAME=rebellis-gke
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=rebellis
POSTGRES_USER=rebellis
POSTGRES_PASSWORD=change_me
REDIS_HOST=localhost
REDIS_PORT=6379
JWT_ISSUER=rebellis
JWT_AUDIENCE=rebellis-clients
JWT_PUBLIC_KEY_PATH=secrets/jwt.pub
```

## One‑Command Deploy (Makefile)
```bash
make terraform-init
make terraform-apply ENV=staging
make deploy-all ENV=staging
make health-check
```

## Health Verification
```bash
curl -fsS http://localhost:8000/health
# {"status":"ok","api":"healthy","db":"connected","redis":"connected"}
```
