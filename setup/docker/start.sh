#!/bin/bash

sleep 3
./venv/bin/python web/manage.py syncdb --noinput
./venv/bin/python web/manage.py collectstatic --noinput
