#!/bin/bash
echo 'installing django-dbindexer'
dbindexer_git_repo=https://github.com/django-nonrel/django-dbindexer.git
${install_location}/venv/bin/pip install git+${dbindexer_git_repo}
