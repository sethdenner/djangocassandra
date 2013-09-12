#!/bin/bash
venv_bin=/srv/knotis/venv/bin

echo 'installing django-nonrel ...'
django_git_repo=https://github.com/Knotis/django.git
${install_location}/venv/bin/pip install git+${django_git_repo}@knotis
