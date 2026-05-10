#!/bin/bash
bash .run/bump_version.sh $1
bash .run/build.sh
bash .run/publish.sh
