#!/bin/bash

set -euo pipefail

coverage run -m pytest -vv --failed-first
coverage report
