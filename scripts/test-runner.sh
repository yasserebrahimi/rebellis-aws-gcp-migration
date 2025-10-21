#!/bin/bash
set -euo pipefail


COV=${COV:-true}


if command -v ruff >/dev/null 2>&1; then ruff check . ; fi
if command -v black >/dev/null 2>&1; then black --check . ; fi
if command -v mypy >/dev/null 2>&1; then mypy src || true ; fi


if command -v pytest >/dev/null 2>&1; then
if [[ "$COV" == "true" ]]; then
pytest -q --maxfail=1 --disable-warnings --cov=src --cov-report=term-missing
else
pytest -q --maxfail=1 --disable-warnings
fi
else
echo "pytest not found" >&2
exit 1
fi