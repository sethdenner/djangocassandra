#!/bin/bash

venv_bin=/srv/knotis/venv/bin

echo 'installing django-haystack ...'
$venv_bin/pip install 'django-haystack>=2.0,<2.1'
#$venv_bin/pip install 'pysolr'
$venv_bin/pip install 'geopy'
