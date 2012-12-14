#!/bin/bash
venv_bin=/srv/knotis/venv/bin

echo 'installing djangotoolbox ...'
djangotoolbox_git_repo=https://github.com/django-nonrel/djangotoolbox.git
${venv_bin}/pip install git+${djangotoolbox_git_repo}@master
