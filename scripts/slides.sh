#!/bin/bash

set -euo pipefail

MD=docs/index.md

# Check the math!
python3 -m doctest $MD

# Update screenshots!
scripts/screenshots.sh

# Slidy worked out of the box; others might be better!
pandoc --to=slidy \
  --include-before-body=docs/include-before-body.html \
  $MD \
  --output docs/index.html \
  --standalone \
&& open docs/index.html
