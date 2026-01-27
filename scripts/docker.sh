#!/bin/bash

set -euo pipefail

TAG='opendp/dp-wizard'
NAME='dp-wizard'
docker build -t $TAG .
docker run --name $NAME -p 8000:8000 $TAG  || \
    echo "If already running, run: docker rm $NAME"

# Since we're not running as daemon, clean up on shutdown.
docker rm $NAME

# TODO: The image starts successfully,
# but I'm not able to connect to http://localhost:8000/
# What am I doing wrong?
