#!/bin/bash

set -euo pipefail

SHARED="pytest -vv --failed-first --durations=5 $@"

if [ -z ${CI+x} ]; then
    echo "Run tests in parallel to save developer time. For single process: 'CI=true scripts/ci.sh'"
    eval "$SHARED --numprocesses=auto --cov=dp_wizard"
else
    echo "Run tests in single process to avoid surprises."
    eval "coverage run -m $SHARED"
    coverage report
fi
