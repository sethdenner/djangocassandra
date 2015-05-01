# Knotis Docker container
#
#

FROM ubuntu:14.04

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
RUN chmod o+rw ${install_location}

COPY setup ${install_location}/setup


ENV CASSANDRA_THRIFT_INTERFACE ${setup_dir}/static/cassandra.thrift
ENV MODWSGI_SCRIPT ${setup_dir}/config/modwsgi/knotis.wsgi
ENV APACHE2_CONFIG ${setup_dir}/config/apache2/dev.knotis.com.conf

RUN apt-get update && ${setup_dir}/installers/install_dependencies.sh

RUN virtualenv venv

RUN ${setup_dir}/installers/install_django.sh
RUN ${setup_dir}/installers/install_beautiful_soup.sh && \
    ${setup_dir}/installers/install_httplib2.sh && \
    ${setup_dir}/installers/install_oauth2.sh && \
    ${setup_dir}/installers/install_mysql_python.sh



RUN . venv/bin/activate && \
    pip install sorl-thumbnail
#pip install git+https://github.com/simlay/sorl-thumbnail.git@fix_cropping_django_1.3

RUN apt-get update && apt-get install -y libgeos-c1 libgeos-3.4.2 && \
    ${setup_dir}/installers/install_django_haystack.sh


RUN apt-get update && \
    ${setup_dir}/installers/install_weasyprint.sh


RUN ${setup_dir}/installers/install_polymodels.sh
RUN ${setup_dir}/installers/install_piston.sh
RUN ${setup_dir}/installers/install_django_autoload.sh

RUN ${setup_dir}/installers/install_thrift.sh

RUN ${setup_dir}/installers/install_apache.sh

# Django Stuff.
#pip install git+https://github.com/django-nonrel/django-permission-backend-nonrel.git@master && \



RUN ${setup_dir}/installers/install_timezones.sh && \
    ${setup_dir}/installers/install_django_extensions.sh && \
    ${setup_dir}/installers/install_crispy_forms.sh && \
    ${setup_dir}/installers/install_django_dbindexer.sh && \
    ${setup_dir}/installers/install_pillow.sh


RUN ${setup_dir}/installers/install_djangorestframework.sh


RUN . venv/bin/activate && \
    ${setup_dir}/installers/install_django_corsheaders.sh && \
    ${setup_dir}/installers/install_django_test_utils.sh && \
    ${setup_dir}/installers/install_django_nose.sh && \
    ${setup_dir}/installers/install_django_user_agent.sh


# For Elasticsearch
RUN . venv/bin/activate &&  pip install pyelasticsearch

RUN ${setup_dir}/installers/install_debug_tools.sh
RUN ${setup_dir}/installers/install_facebook.sh
RUN ${setup_dir}/installers/install_twitter.sh
RUN ${setup_dir}/installers/install_stripe.sh

RUN . venv/bin/activate && \
    pip uninstall -y cassandra-driver && \
    pip install cassandra-driver



EXPOSE 8000
EXPOSE 443
EXPOSE 80

VOLUME ${install_location}/logs
VOLUME ${install_location}/app
VOLUME ${install_location}/static
VOLUME ${install_location}/web
VOLUME ${install_location}/run/eggs

COPY setup/docker/start.sh ${install_location}/start.sh

RUN chown -R ${ADMIN_USER}:${ADMIN_GROUP} ${install_location} && \
    chmod -R 755 ${install_location}
#usermod -m -d ${install_location} ${ADMIN_USER}

RUN echo source ${install_location}/venv/bin/activate >> ~/.bashrc && \
    echo source ${install_location}/venv/bin/activate >> ~/.bash_profile
