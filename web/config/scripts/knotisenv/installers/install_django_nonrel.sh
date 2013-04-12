#!/bin/bash
venv_bin=/srv/knotis/venv/bin

echo 'installing django-nonrel ...'
django_git_repo=https://github.com/django-nonrel/django-nonrel.git
${venv_bin}/pip install git+${django_git_repo}@master
