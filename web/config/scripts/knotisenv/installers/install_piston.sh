#!/bin/bash
venv_bin=/srv/knotis/venv/bin
echo 'installing django-piston ...'
${venv_bin}/pip install hg+https://bitbucket.org/jespern/django-piston-oauth2
