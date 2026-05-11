#!/bin/bash

run() {
  echo "+ $*"
  "$@"
}

run mkdocs serve
