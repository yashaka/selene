#!/bin/bash

run() {
  echo "+ $*"
  "$@"
}

run black . --check --diff
