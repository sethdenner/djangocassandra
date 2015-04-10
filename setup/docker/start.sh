#!/bin/bash

chmod -R o+rw ${install_location}

./venv/bin/python web/manage.py runserver 0.0.0.0:8000 & disown
service apache2 start & disown

tail -f /var/log/apache2/access.log
