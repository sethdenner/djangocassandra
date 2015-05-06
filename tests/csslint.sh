#!/bin/bash

csslint --format=lint-xml > csslint.xml $(find web/ -name '*.css' -type f) || exit 0
