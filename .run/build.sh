#!/bin/bash

run() {
  echo "+ $*"
  "$@"
}

run poetry build
