#!/bin/bash
set -euo pipefail


read -r -p "This will prune stopped containers, unused networks/images/volumes. Continue? [y/N] " ans
if [[ "${ans,,}" != "y" ]]; then
echo "Aborted"; exit 0
fi


# Python artifacts
find . -type d -name "__pycache__" -prune -exec rm -rf {} +
rm -rf .pytest_cache .mypy_cache dist build *.egg-info || true


# Docker prune
if command -v docker >/dev/null 2>&1; then
docker system prune -af --volumes || true
fi


echo "Cleanup complete"