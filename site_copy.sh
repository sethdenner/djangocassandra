#!/bin/bash

cp -a ~/knotis.com/web /srv/knotis/
chmod -R 755 /srv/knotis/
chown -R knotis:knotis /srv/knotis/
/srv/knotis/venv/bin/python /srv/knotis/web/manage.py collectstatic --noinput
service apache2 reload
