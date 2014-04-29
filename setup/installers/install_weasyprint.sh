#!/bin/bash

venv_bin=/srv/knotis/venv/bin

echo 'installing WeasyPrint...'
apt-get -y install python-dev python-pip python-lxml libcairo2 libpango1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

$venv_bin/pip install WeasyPrint
