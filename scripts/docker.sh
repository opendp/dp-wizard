#!/bin/bash

set -euo pipefail

TAG='opendp/dp-wizard'
NAME='dp-wizard'
docker build -t $TAG .
# Remove any previous container with the same name (ignore errors)
docker rm -f "$NAME" >/dev/null 2>&1 || true

docker run --name "$NAME" -p 8000:8000 "$TAG" \
  shiny run --host 0.0.0.0 dp_wizard.app
# Since we're not running as daemon, clean up on shutdown.
docker rm $NAME

# TODO: The image starts successfully,
# but I'm not able to connect to http://localhost:8000/
# What am I doing wrong?
