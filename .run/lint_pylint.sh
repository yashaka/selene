#!/bin/bash

run() {
  echo "+ $*"
  "$@"
}

run touch __init__.py
run pylint "$(pwd)" --disable="$(cat .pylint-disabled-rules)" --ignore-paths=\.venv --ignore-patterns=.*\.pyi -r n
run rm __init__.py
