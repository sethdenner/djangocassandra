#!/bin/bash

venv_bin=/srv/knotis/venv/bin

echo 'installing django-haystack ...'
apt-get install -y libgeos-c1 libgeos-3.2.2
$venv_bin/pip install --no-deps 'django-haystack>=2.0,<2.1'
#$venv_bin/pip install 'pysolr'
$venv_bin/pip install 'geopy'
