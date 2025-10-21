#!/bin/bash
set -euo pipefail


API_URL=${API_URL:-"http://localhost:8000/health"}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
REDIS_HOST=${REDIS_HOST:-localhost}
REDIS_PORT=${REDIS_PORT:-6379}


BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'
info(){ echo -e "${BLUE}[INFO]${NC} $1"; }
ok(){ echo -e "${GREEN}[OK]${NC} $1"; }
fail(){ echo -e "${RED}[FAIL]${NC} $1"; exit 1; }


info "Checking API: $API_URL"
if curl -fsS "$API_URL" >/dev/null; then ok "API healthy"; else fail "API unreachable"; fi


info "Checking Postgres ${DB_HOST}:${DB_PORT}"
if command -v pg_isready >/dev/null 2>&1; then
pg_isready -h "$DB_HOST" -p "$DB_PORT" && ok "Postgres ready" || fail "Postgres not ready"
else
info "pg_isready not available; skipping"
fi


info "Checking Redis ${REDIS_HOST}:${REDIS_PORT}"
if command -v redis-cli >/dev/null 2>&1; then
redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping | grep -q PONG && ok "Redis PONG" || fail "Redis not responding"
else
info "redis-cli not available; skipping"
fi


# Optional: GPU check
if command -v nvidia-smi >/dev/null 2>&1; then
info "GPU detected:"
nvidia-smi || true
fi