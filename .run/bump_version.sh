#!/bin/bash

run() {
  echo "+ $*"
  "$@"
}

version=$1
if [[ $1 == '' ]]; then
  echo -n 'please specify selene version: '
  read text
  version=$text
fi
run poetry version "$version"
echo "+ grep '^version = \"*\"' pyproject.toml | cut -d'\"' -f2"
new_vers=$(grep "^version = \"*\"" pyproject.toml | cut -d'"' -f2)
run sed -i "" "s/__version__ = .*/__version__ = \'${new_vers}\'/g" selene/__init__.py
