#!/bin/bash

echo 'installing Debug Tools...'
${install_location}/venv/bin/pip install ipdb ipython cqlsh
${install_location}/venv/bin/pip install --no-deps nose
