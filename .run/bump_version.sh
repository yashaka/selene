#!/bin/bash
version=$1
if [[ $1 == '' ]]; then
  echo -n 'please specify selene version: '
  read text
  version=$text
fi
poetry version $version
new_vers=$(cat pyproject.toml | grep "^version = \"*\"" | cut -d'"' -f2)
sed -i "" "s/__version__ = .*/__version__ = \'${new_vers}\'/g" selene/__init__.py
