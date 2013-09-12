#!/bin/bash
venv_bin=/srv/knotis/venv/bin

echo 'installing djangotoolbox ...'
djangotoolbox_git_repo=https://github.com/django-nonrel/djangotoolbox.git
${install_location}/venv/bin/pip install git+${djangotoolbox_git_repo}@toolbox-1.3
