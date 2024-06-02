#!/bin/bash

pycodestyle $(pwd) --ignore=E501,W503,E402,E731,E203,E704,W605 --exclude=.venv
