#!/bin/bash

run() {
  echo "+ $*"
  "$@"
}

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYPROJECT="$ROOT_DIR/pyproject.toml"
PYPROJECT_BACKUP="$ROOT_DIR/pyproject.toml.bak.codex"
PYPI_README="$ROOT_DIR/README.pypi.md"
MODE="${1:-}"

cleanup() {
  if [[ -f "$PYPROJECT_BACKUP" ]]; then
    mv "$PYPROJECT_BACKUP" "$PYPROJECT"
  fi
  rm -f "$PYPI_README"
}

build_for_pypi() {
  trap cleanup EXIT

  run cp "$ROOT_DIR/README.md" "$PYPI_README"
  run cp "$PYPROJECT" "$PYPROJECT_BACKUP"

  # Convert local markdown anchors like (#section) to absolute GitHub links
  # so links remain clickable in PyPI rendered description.
  run perl -0pi -e 's/\]\(#([^)]+)\)/](https:\/\/github.com\/yashaka\/selene#\1)/g' "$PYPI_README"

  if ! rg -q '^readme = "README.md"$' "$PYPROJECT"; then
    echo 'Expected `readme = "README.md"` in pyproject.toml' >&2
    exit 1
  fi

  run perl -0pi -e 's/^readme = "README\.md"$/readme = "README.pypi.md"/m' "$PYPROJECT"
  cd "$ROOT_DIR"
  run poetry build
  run twine check dist/*
}

build_default() {
  cd "$ROOT_DIR"
  run poetry build
}

case "$MODE" in
  --for-pypi)
    build_for_pypi
    ;;
  "")
    build_default
    ;;
  *)
    echo "Unknown option: $MODE" >&2
    echo "Usage: bash .run/build.sh [--for-pypi]" >&2
    exit 1
    ;;
esac
