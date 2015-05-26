#!/bin/bash

docker build -t knotis/web:1.7 .
docker-compose up -d
sleep 5

export CONTAINER_NAME=django17migrationsimlay_web_1

alias knotis_exec="docker exec $CONTAINER_NAME"
knotis_exec find /srv/knotis/venv/ -type f | grep oauth2_provider | grep '/migrations' | xargs rm
knotis_exec /srv/knotis/venv/bin/python /srv/knotis/web/manage.py makemigrations
knotis_exec /srv/knotis/venv/bin/python /srv/knotis/web/manage.py migrate
knotis_exec /srv/knotis/venv/bin/python /srv/knotis/web/manage.py loaddata web/knotis/contrib/hack/fixtures/content_types.json
knotis_exec /srv/knotis/venv/bin/python /srv/knotis/web/manage.py loaddata web/knotis/contrib/product/fixtures/products.json
knotis_exec /srv/knotis/venv/bin/python /srv/knotis/web/manage.py loaddata web/knotis/contrib/rest_framework/fixtures/oauth_client.json
knotis_exec /srv/knotis/venv/bin/python /srv/knotis/web/manage.py test --verbosity=2 --with-xunit --xunit-file=web/nosetests.xml --with-xcoverage --cover-package=knotis --cover-tests --xcoverage-file=web/coverage.xml
exit 0
