#!/bin/bash
pylint -f parseable web/ > pylint.log || exit 0
