#!/bin/bash
set -euo pipefail


ENVIRONMENT=${1:-staging}
PROJECT_NAME="rebellis"
NAMESPACE="rebellis-${ENVIRONMENT}"


RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
msg(){ echo -e "$1"; }


msg "${YELLOW}Attempting rollback for ${PROJECT_NAME} (${ENVIRONMENT})...${NC}"


if [[ "$ENVIRONMENT" == "production" ]]; then
if command -v helm >/dev/null 2>&1; then
helm rollback "$PROJECT_NAME" --namespace "$NAMESPACE" || msg "${RED}Helm rollback failed${NC}"
else
msg "${RED}helm not found${NC}"
exit 1
fi
else
if command -v docker >/dev/null 2>&1; then
docker compose down || true
docker compose up -d || true
else
msg "${RED}docker not found${NC}"
exit 1
fi
fi


msg "${GREEN}Rollback routine finished${NC}"