#!/bin/bash
set -euo pipefail

bash .run/bump_version.sh "${1:-patch}"
bash .run/build.sh --for-pypi
bash .run/publish.sh
