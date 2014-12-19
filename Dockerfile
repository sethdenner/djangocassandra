# Knotis Docker container
#
#

FROM ubuntu:12.04

RUN apt-get update && apt-get install -y libboost-dev libboost-test-dev libboost-program-options-dev libevent-dev libtool flex bison pkg-config g++ libssl-dev python python-dev python-setuptools python-software-properties python-support python-twisted make automake autoconf acl gcc git mercurial libmysqlclient-dev python-pip libjpeg8 libjpeg-dev libfreetype6 libfreetype6-dev zlib1g-dev python-virtualenv

RUN mkdir /knotis.com
WORKDIR /knotis.com

RUN virtualenv venv

RUN . venv/bin/activate && \
    pip install BeautifulSoup && \
    pip install httplib2 && \
    pip install oauth2 && \
    pip install --upgrade distribute && \
    pip install MySQL-python

RUN . venv/bin/activate && \
    pip install PIL

RUN . venv/bin/activate && \
    pip install git+https://github.com/Knotis/sorl-thumbnail.git@fix_cropping

RUN . venv/bin/activate && \
    pip install --no-deps 'django-haystack>=2.0,<2.1' && \
    apt-get update && apt-get install -y libgeos-c1 libgeos-3.2.2 && \
    pip install 'geopy'

RUN apt-get update && \
    apt-get -y install python-lxml libcairo2 libpango1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info libxslt-dev && \
    . venv/bin/activate && \
    pip install WeasyPrint && \
    pip install markdown && \
    pip install defusedxml && \
    pip install PyYAML && \
    pip install nose && \
    pip install twitter==1.14.3 && \
    pip install facebook-sdk==0.4.0 && \
    pip install stripe==1.14.0 && \
    pip install ipdb && \
    pip install ipython


COPY setup /knotis.com/setup

ENV setup_dir /knotis.com/setup
ENV install_location /knotis.com
ENV CASSANDRA_THRIFT_INTERFACE ${setup_dir}/static/cassandra.thrift
ENV MODWSGI_SCRIPT ${setup_dir}/config/modwsgi/knotis.wsgi
ENV APACHE2_CONFIG ${setup_dir}/config/apache2/docker.knotis.com

RUN mkdir /knotis.com/logs /knotis.com/app /knotis.com/static

RUN . venv/bin/activate && \
    pip install ${setup_dir}/static/django-nonrel-1.3.tar.gz && \
    pip install ${setup_dir}/static/djangotoolbox.tar.gz && \
    pip install git+https://github.com/django-nonrel/django-permission-backend-nonrel.git@master && \
    pip install git+https://github.com/django-nonrel/django-dbindexer.git@dbindexer-1.3 && \
    pip install git+https://github.com/brosner/django-timezones.git && \
    pip install git+https://github.com/maraujop/django-crispy-forms.git@master && \
    pip install ${setup_dir}/static/django-extensions-1.3-support.tar.gz && \
    pip install --no-deps django-cors-headers && \
    pip install djangorestframework==2.3.13 && \
    pip install django-filter && \
    pip install django-oauth-plus && \
    pip install django-guardian && \
    pip install -U --no-deps git+https://github.com/Knotis/doac@knotis && \
    pip install django-test-utils && \
    pip install --no-deps django_nose && \
    pip install pyelasticsearch


RUN . venv/bin/activate && \
    pip install hg+https://bitbucket.org/twanschik/django-autoload && \
    pip install git+https://github.com/maraujop/django-crispy-forms.git@master && \
    pip install ${setup_dir}/static/django-polymodels-1.3-support.tar.gz && \
    pip install hg+https://bitbucket.org/jespern/django-piston-oauth2

# Because numpy is huge.
# This shit ain't used.
# RUN pip install numpy

RUN . venv/bin/activate && \
    apt-get update && ${setup_dir}/installers/install_thrift.sh

RUN . venv/bin/activate && \
    ${setup_dir}/installers/install_django_cassandra.sh

RUN ${setup_dir}/installers/install_apache.sh

EXPOSE 8000

#ENTRYPOINT /knotis.com/venv/bin/python /knotis.com/web/manage.py runserver 0.0.0.0:8000
