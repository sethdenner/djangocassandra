#!/bin/bash

#jshint --jslint-reporter > jslint.xml  $(find web/ -name '*.js' -type f) || exit 0
jshint --jslint-reporter  > jslint.xml $(find web/ -name '*.js' -type f) || exit 0


