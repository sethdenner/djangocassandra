#!/bin/bash

pep8 $(find web -name "*.py" -print) > pep8.log || exit 0
