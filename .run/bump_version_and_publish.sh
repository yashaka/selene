#!/bin/bash
bash .run/bump_version.sh $1
poetry publish --build
