#!/bin/bash

touch __init__.py
pylint $(pwd) --disable="$(cat .pylint-disabled-rules)" --ignore-patterns=.venv
rm __init__.py
