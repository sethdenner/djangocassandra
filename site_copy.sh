#!/bin/bash

cp -a ~/knotis.com/web /srv/knotis/
(
    cd /srv/knotis/
    venv/bin/python web/manage.py collectstatic --noinput
)
chown -R knotis:knotis /srv/knotis/
