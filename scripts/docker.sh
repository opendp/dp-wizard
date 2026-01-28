#!/bin/bash

set -euo pipefail

NAME="dp-wizard"
# Use xargs to strip any trailing whitespace:
VERSION=`cat dp_wizard/VERSION | xargs`
TAG="mccalluc/$NAME:$VERSION"
LATEST="mccalluc/$NAME:latest"

echo "Building $TAG..."
docker build -t $TAG .
# Remove any previous container with the same name (ignore errors):
docker rm -f "$NAME" >/dev/null 2>&1 || true

echo "Confirm that the image works, then ctrl-C:"
docker run --name "$NAME" -p 8000:8000 "$TAG"
# Since we're not running as daemon, clean up on shutdown:
docker rm $NAME

echo "If everything looks good: docker tag $TAG $LATEST; docker image push $TAG; docker image push $LATEST"
