#!/bin/bash

run() {
  echo "+ $*"
  "$@"
}

run poetry publish
