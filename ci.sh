#!/bin/bash

set -euo pipefail

pytest -vv --failed-first --numprocesses=auto --cov=dp_wizard
