#!/bin/bash

echo 'installing django-permission-backend-nonrel ...'
perm_backend_nonrel_git=https://github.com/django-nonrel/django-permission-backend-nonrel.git
${install_location}/venv/bin/pip install git+${perm_backend_nonrel_git}@master
