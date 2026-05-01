#!/bin/bash
set -euo pipefail

run() {
  echo "+ $*"
  "$@"
}

run bash .run/bump_version.sh "${1:-patch}"
run bash .run/build.sh --for-pypi
run bash .run/publish.sh
