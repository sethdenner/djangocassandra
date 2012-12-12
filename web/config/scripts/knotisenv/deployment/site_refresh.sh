#!/bin/bash

venv_bin=/srv/knotis/venv/bin
manage="${venv_bin}/python /srv/knotis/app/web/manage.py"

${manage} collectstatic --noinput
${manage} syncdb

service apache2 reload
