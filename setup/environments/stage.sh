#!/bin/bash

export ENVIRONMENT_NAME=stage
export KNOTIS_WEB=$(readlink -e ../web)
export MODWSGI_SCRIPT=$(readlink -e ./config/modwsgi/knotis.wsgi)
export APACHE2_CONFIG=$(readlink -e ./config/apache2/stage.knotis.com)
export CASSANDRA_CONFIG=$(readlink -e ./config/cassandra/stage.cassandra-2.0.0.yaml)
export CASSANDRA_ENV=$(readlink -e ./config/cassandra/stage.cassandra-env-2.0.0.sh)
export CASSANDRA_THRIFT_INTERFACE=$(readlink -e ./static/cassandra.thrift)
export DEFAULT_INSTALL_LOCATION=/srv/knotis
export ADMIN_USER=knotis
export ADMIN_GROUP=knotis
export INSTALLERS=(
    install_dependencies.sh
    install_virtualenv.sh
    install_java.sh
    install_cassandra.sh
    install_apache.sh
    install_thrift.sh
    install_httplib2.sh
    install_oauth2.sh
    install_mysql_python.sh
    install_numpy.sh
    install_django_nonrel.sh
    install_djangotoolbox.sh
    install_django_permission_backend_nonrel.sh
    install_django_dbindexer.sh
    install_django_extensions.sh
    install_django_cassandra.sh
    install_django_autoload.sh
    install_crispy_forms.sh
    install_polymodels.sh
    install_piston.sh
    install_pil.sh
    install_sorlthumbnail.sh
    install_beautiful_soup.sh
    install_timezones.sh
    install_elasticsearch.sh
    install_django_haystack.sh
    install_weasyprint.sh
    install_django_corsheaders.sh
    install_djangorestframework.sh
    install_django_test_utils.sh
    install_geopy.sh
)
