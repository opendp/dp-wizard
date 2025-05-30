#!/bin/bash

die() {
  printf '%s\n' "$*" >&2
  exit 1
}

set -euo pipefail

echo "Check git..."

git diff --exit-code || die "There should be no local modifications."

BRANCH=`git rev-parse --abbrev-ref HEAD`
[ "$BRANCH" = "main" ] || die "Current branch should be 'main', not '$BRANCH'."

git pull

echo "Check tests..."

CI='true' scripts/ci.sh --exitfirst || die "Tests should pass"

echo "Push..."

git branch -D cloud-deployment
git checkout -b cloud-deployment
git push -f origin cloud-deployment

echo "Redeployed!"

git checkout main
