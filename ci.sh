#!/bin/bash

set -euo pipefail

coverage run -m pytest -v
coverage report
