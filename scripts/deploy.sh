#!/bin/bash

die() {
  printf '%s\n' "$*" >&2
  exit 1
}

set -euo pipefail

echo "Check git..."

git pull
git diff --exit-code || die "There should be no local modifications."

BRANCH=`git rev-parse --abbrev-ref HEAD`
[ "$BRANCH" = "main" ] || die "Current branch should be 'main', not '$BRANCH'."

echo "Check tests..."

CI='true' scripts/ci.sh --exitfirst || die "Tests should pass"

echo "Push..."

git push -f origin main:cloud-deployment

echo "Redeployed!"
