#!/bin/bash
set -euo pipefail

run_black_on_all() {
  echo "Running black on all files (fallback mode)"
  black . --check --diff
}

get_changed_python_files() {
  local diff_base="${1:-}"
  if [[ -z "$diff_base" ]]; then
    return 0
  fi

  git diff --name-only --diff-filter=ACMR "${diff_base}...HEAD" -- '*.py'
}

if [[ "${GITHUB_EVENT_NAME:-}" == "pull_request" && -n "${GITHUB_BASE_REF:-}" ]]; then
  git fetch --no-tags --depth=1 origin "${GITHUB_BASE_REF}"
  BASE_COMMIT="$(git merge-base HEAD FETCH_HEAD || true)"
elif [[ "${GITHUB_EVENT_NAME:-}" == "push" && -n "${GITHUB_EVENT_BEFORE:-}" ]]; then
  BASE_COMMIT="${GITHUB_EVENT_BEFORE}"
else
  BASE_COMMIT=""
fi

if [[ -z "${BASE_COMMIT}" ]]; then
  run_black_on_all
  exit 0
fi

mapfile -t CHANGED_PYTHON_FILES < <(get_changed_python_files "${BASE_COMMIT}")

if [[ "${#CHANGED_PYTHON_FILES[@]}" -eq 0 ]]; then
  echo "No changed Python files in diff, skipping black"
  exit 0
fi

echo "Running black on changed files:"
printf '%s\n' "${CHANGED_PYTHON_FILES[@]}"
black --check --diff "${CHANGED_PYTHON_FILES[@]}"
