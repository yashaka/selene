#!/bin/bash

run() {
  echo "+ $*"
  "$@"
}

run mypy . --follow-imports=skip --ignore-missing-imports
