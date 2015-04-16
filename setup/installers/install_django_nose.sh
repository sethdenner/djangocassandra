#!/bin/bash

venv_bin=/srv/knotis/venv/bin

echo 'installing django_nose...'

$venv_bin/pip install 'django-nose==1.3'
