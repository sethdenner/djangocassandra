#!/bin/bash

docker build -t knotis/web .
docker-compose up -d
sleep 5
docker exec knotiscom_web_1 /srv/knotis/venv/bin/python /srv/knotis/web/manage.py syncdb --noinput
docker exec knotiscom_web_1 /srv/knotis/venv/bin/python /srv/knotis/web/manage.py test --verbosity=1 --with-xunit --xunit-file=web/nosetests.xml --with-xcoverage --cover-package=knotis --cover-tests --xcoverage-file=web/coverage.xml
exit 0
