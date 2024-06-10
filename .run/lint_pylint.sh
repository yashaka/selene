#!/bin/bash

touch __init__.py
pylint $(pwd) --disable="$(cat .pylint-disabled-rules)" --ignore-paths=\.venv --ignore-patterns=.*\.pyi -r n
rm __init__.py
