# Knotis Docker container
#
#

FROM ubuntu:12.04

ENV install_location /srv/knotis
ENV setup_dir ${install_location}/setup

RUN mkdir ${install_location}
WORKDIR ${install_location}
ENV ADMIN_USER knotis
ENV ADMIN_GROUP knotis
ENV CASSANDRA_THRIFT_INTERFACE ${setup_dir}/static/cassandra.thrift
ENV MODWSGI_SCRIPT ${setup_dir}/config/modwsgi/knotis.wsgi
ENV APACHE2_CONFIG ${setup_dir}/config/apache2/dev.knotis.com


RUN id -g ${ADMIN_GROUP} > /dev/null 2>&1 || groupadd --system ${ADMIN_GROUP}
RUN id -u ${ADMIN_USER} > /dev/null 2>&1 || useradd --system -N ${ADMIN_USER}
RUN chown -R ${ADMIN_USER}:${ADMIN_GROUP} ${install_location}
COPY setup ${install_location}/setup


RUN apt-get update && apt-get install -y libboost-dev libboost-test-dev libboost-program-options-dev libevent-dev libtool flex bison pkg-config g++ libssl-dev python python-dev python-setuptools python-software-properties python-support python-twisted make automake autoconf acl gcc git mercurial libmysqlclient-dev python-pip libjpeg8 libjpeg-dev libfreetype6 libfreetype6-dev zlib1g-dev python-virtualenv

RUN apt-get update && ${setup_dir}/installers/install_dependencies.sh
RUN apt-get update && ${setup_dir}/installers/install_virtualenv.sh

RUN ${setup_dir}/installers/install_apache.sh

RUN ${setup_dir}/installers/install_thrift.sh

RUN ${setup_dir}/installers/install_beautiful_soup.sh && \
    ${setup_dir}/installers/install_httplib2.sh && \
    ${setup_dir}/installers/install_oauth2.sh && \
    ${setup_dir}/installers/install_mysql_python.sh


RUN ${setup_dir}/installers/install_django_nonrel.sh
RUN ${setup_dir}/installers/install_djangotoolbox.sh
RUN ${setup_dir}/installers/install_django_permission_backend_nonrel.sh
RUN ${setup_dir}/installers/install_django_dbindexer.sh
RUN ${setup_dir}/installers/install_django_extensions.sh
RUN ${setup_dir}/installers/install_django_cassandra.sh
RUN ${setup_dir}/installers/install_django_autoload.sh

RUN ${setup_dir}/installers/install_crispy_forms.sh
RUN ${setup_dir}/installers/install_polymodels.sh
RUN ${setup_dir}/installers/install_piston.sh
RUN ${setup_dir}/installers/install_pillow.sh
RUN ${setup_dir}/installers/install_sorlthumbnail.sh
RUN ${setup_dir}/installers/install_timezones.sh
RUN ${setup_dir}/installers/install_django_haystack.sh
RUN ${setup_dir}/installers/install_weasyprint.sh

RUN ${setup_dir}/installers/install_django_corsheaders.sh
RUN ${setup_dir}/installers/install_djangorestframework.sh
RUN ${setup_dir}/installers/install_django_test_utils.sh
RUN ${setup_dir}/installers/install_django_user_agent.sh

RUN ${setup_dir}/installers/install_twitter.sh
RUN ${setup_dir}/installers/install_facebook.sh
RUN ${setup_dir}/installers/install_stripe.sh
RUN ${setup_dir}/installers/install_django_nose.sh
RUN ${setup_dir}/installers/install_debug_tools.sh

# Elastic Search part.
RUN . venv/bin/activate && pip install pyelasticsearch

EXPOSE 8000
EXPOSE 80

VOLUME ${install_location}/logs
VOLUME ${install_location}/app
VOLUME ${install_location}/static
VOLUME ${install_location}/web
VOLUME ${install_location}/run/eggs

COPY setup/docker/start.sh ${install_location}/start.sh

RUN chmod o+rw ${install_location} && \
    chmod o+rwx ${install_location}/start.sh && \
    usermod -m -d ${install_location} ${ADMIN_USER}

RUN echo source ${install_location}/venv/bin/activate >> ~/.bashrc && \
    echo source ${install_location}/venv/bin/activate >> ~/.bash_profile
