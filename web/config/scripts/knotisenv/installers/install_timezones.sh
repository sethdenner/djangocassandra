#!/bin/bash
venv_bin=/srv/knotis/venv/bin

echo 'installing django-timezones ...'
djangotimezones_git_repo=https://github.com/brosner/django-timezones.git
${venv_bin}/pip install git+${djangotimezones_git_repo}
