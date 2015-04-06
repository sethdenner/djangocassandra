#!/bin/bash

sleep 3
./venv/bin/python web/manage.py migrate --noinput
./venv/bin/python web/manage.py collectstatic --noinput


chown -R ${ADMIN_USER}:${ADMIN_GROUP} ${install_location}

chmod -R u+rw ${install_location}

./venv/bin/python web/manage.py runserver 0.0.0.0:8000 & disown
service apache2 start & disown

tail -f /var/log/apache2/access.log
