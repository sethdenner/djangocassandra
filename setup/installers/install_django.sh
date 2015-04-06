#!/bin/bash
venv_bin=/srv/knotis/venv/bin

echo 'installing django ...'

${install_location}/venv/bin/pip install cassandra-driver
${install_location}/venv/bin/pip install git+https://github.com/Knotis/djangocassandra.git

${install_location}/venv/bin/pip install --upgrade git+https://github.com/sethdenner/django.git@custom-autofield
${install_location}/venv/bin/pip install --upgrade git+https://github.com/Knotis/djangotoolbox.git
