#!/bin/bash

set -euo pipefail

NAME="dp-wizard"
TAG="opendp/$NAME"

docker build -t $TAG .
# Remove any previous container with the same name (ignore errors)
docker rm -f "$NAME" >/dev/null 2>&1 || true

docker run --name "$NAME" -p 8000:8000 "$TAG"
# Since we're not running as daemon, clean up on shutdown.
docker rm $NAME
