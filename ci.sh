#!/bin/bash

set -euo pipefail

if [ -z ${CI+x} ]; then
    echo "Run tests in parallel to save developer time. For single process: 'CI=true ./ci.sh'"
    pytest -vv --failed-first --numprocesses=auto --cov=dp_wizard
else
    echo "Run tests in single process to avoid surprises."
    coverage run -m pytest -vv --failed-first
    coverage report
fi
