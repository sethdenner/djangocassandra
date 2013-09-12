#!/bin/bash

export ENVIRONMENT_NAME=next
export MODWSGI_SCRIPT=$(readlink -e ./config/modwsgi/knotis.wsgi)
export APACHE2_CONFIG=$(readlink -e ./config/apache2/next.knotis.com)
export CASSANDRA_CONFIG=$(readlink -e ./config/cassandra/cassandra.yaml)
export CASSANDRA_THRIFT_INTERFACE=$(readlink -e ./config/cassandra/cassandra.thrift)
export DEFAULT_INSTALL_LOCATION=/srv/knotis
export ADMIN_USER=knotis
export ADMIN_GROUP=knotis
export INSTALLERS=(
#    install_dependencies.sh
#    install_virtualenv.sh
#    install_java.sh
#    install_cassandra.sh
#    install_apache.sh
#    install_thrift.sh
#    install_httplib2.sh
#    install_oauth2.sh
#    install_mysql_python.sh
#    install_numpy.sh
#    install_django_nonrel.sh
#    install_djangotoolbox.sh
#    install_django_permission_backend_nonrel.sh
#    install_django_dbindexer.sh
#    install_django_extensions.sh
    install_django_cassandra.sh
    install_django_autoload.sh
    install_crispy_forms.sh
    install_polymodels.sh
    install_piston.sh
    install_pil.sh
    install_sorlthumbnail.sh
    install_timezones.sh
)
