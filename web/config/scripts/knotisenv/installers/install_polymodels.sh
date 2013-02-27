#!/bin/bash
venv_bin=/srv/knotis/venv/bin

echo 'installing polymodels ...'
polymodels_git_repo=https://github.com/charettes/django-polymodels.git
${venv_bin}/pip install git+${polymodels_git_repo}@master
