#!/bin/bash

export ENVIRONMENT_NAME=next
export MODWSGI_SCRIPT=knotis.wsgi
export APACHE2_CONFIG=next.knotis.com
export CASSANDRA_CONFIG=cassandra.yaml
export DEFAULT_INSTALL_LOCATION=/srv/knotis
export ADMIN_USER=knotis
export ADMIN_GROUP=knotis
export INSTALLERS=(
    install_dependencies.sh
    install_java.sh
    install_cassandra.sh
    install_apache.sh
)
