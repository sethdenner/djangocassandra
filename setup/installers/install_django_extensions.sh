#!/bin/bash
venv_bin=/srv/knotis/venv/bin

echo 'installing django_extensions ...'
django_extensions_git_repo=https://github.com/django-extensions/django-extensions.git
${install_location}/venv/bin/pip install git+${django_extensions_git_repo}@master
