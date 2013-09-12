#!/bin/bash
echo 'installing django-autoload ...'
autoload_hg_repo=https://bitbucket.org/twanschik/django-autoload
${install_location}/venv/bin/pip install hg+${autoload_hg_repo}
