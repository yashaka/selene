#!/bin/bash

run() {
  echo "+ $*"
  "$@"
}

run bash .run/bump_version.sh "$1"
run bash .run/build.sh
run bash .rub/publish.sh
