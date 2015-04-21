#!/bin/bash

./venv/bin/python web/manage.py collectstatic --noinput

chmod -R o+rw ${install_location}

service apache2 start & disown

tail -f /var/log/apache2/access.log
