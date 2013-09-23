#!/bin/bash
echo 'installing polymodels ...'
polymodels_git_repo=https://github.com/charettes/django-polymodels.git
${install_location}/venv/bin/pip install git+${polymodels_git_repo}@master
