#!/bin/bash

die() {
  printf '%s\n' "$*" >&2
  exit 1
}

set -euo pipefail

git diff --exit-code || die "There should be no local modifications."

BRANCH=`git rev-parse --abbrev-ref HEAD`
[ "$BRANCH" != "main" ] || die "Current branch should be 'main', not '$BRANCH'."

scripts/ci.sh || die "Tests should pass"

git push -f origin cloud-deployment
