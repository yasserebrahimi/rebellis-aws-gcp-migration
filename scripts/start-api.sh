#!/usr/bin/env bash
set -euo pipefail
APP=${APP_MODULE:-src.api.main:app}
echo "[start-api] APP=${APP}"
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
ENVIRONMENT=${ENVIRONMENT:-production}
DEBUG=${DEBUG:-false}
if [[ "$ENVIRONMENT" == "production" || "${GUNICORN:-1}" == "1" ]]; then
  exec gunicorn "${APP}" --config ./gunicorn.conf.py --bind "${HOST}:${PORT}"
else
  ARGS=( "${APP}" "--host" "${HOST}" "--port" "${PORT}" "--log-level" "${LOG_LEVEL:-info}" )
  if [[ "${DEBUG}" == "true" ]]; then ARGS+=( "--reload" ); fi
  exec uvicorn "${ARGS[@]}"
fi
