#!/bin/bash

set -euo pipefail

SHARED="pytest -vv --failed-first --durations=5 $@"

if [ -z ${CI+x} ]; then
    echo "Run tests in parallel to save developer time. For single process: 'CI=true scripts/ci.sh'"
    # Clean up to avoid spurious errors:
    autoflake8 .
    isort .
    black .
    eval "$SHARED --numprocesses=auto --cov=."
else
    echo "Run tests in single process to avoid surprises."
    eval "coverage run -m $SHARED"
    coverage report
fi
