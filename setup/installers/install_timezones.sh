#!/bin/bash
echo 'installing django-timezones ...'
djangotimezones_git_repo=https://github.com/brosner/django-timezones.git
${install_location}/venv/bin/pip install git+${djangotimezones_git_repo}
