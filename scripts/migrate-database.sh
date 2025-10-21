#!/bin/bash
set -euo pipefail


ACTION=${1:-upgrade}
REVISION=${2:-head}


if ! command -v alembic >/dev/null 2>&1; then
echo "alembic not found in PATH" >&2
exit 1
fi


case "$ACTION" in
upgrade)
alembic upgrade "$REVISION" ;;
downgrade)
alembic downgrade "$REVISION" ;;
revision)
alembic revision --autogenerate -m "${3:-auto}" ;;
current)
alembic current ;;
history)
alembic history ;;
*)
echo "Usage: $0 [upgrade|downgrade|revision|current|history] [rev]" ;;
esac