#/bin/bash

service cassandra stop
rm -r /var/lib/cassandra/*

service cassandra start
sleep 5

/srv/knotis/venv/bin/python /srv/knotis/web/manage.py syncdb --noinput
