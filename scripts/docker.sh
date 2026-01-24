#!/bin/bash

set -euo pipefail

docker build -t opendp/dp-wizard .
docker run --name dp-wizard -p 8000:8000 opendp/dp-wizard

# TODO: The image starts successfully,
# but I'm not able to connect to http://localhost:8000/
# What am I doing wrong?
