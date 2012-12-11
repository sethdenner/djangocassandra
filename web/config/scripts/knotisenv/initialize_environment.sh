#!/bin/bash

# run with su privs

installer_dir="$(pwd)/installers"


# install required packages
apt-get -y install python python-dev python-setuptools
easy_install virtualenv virtualenvwrapper pip automake autoconf acl gcc git mercurial libmysqlclient-dev

# create temp directory to work in
rm -rf /tmp/knotis 2> /dev/null
mkdir -p /tmp/knotis
cd /tmp/knotis

# install virtual environment
pip install virtualenv

mkdir -p /srv/knotis /srv/knotis/logs /srv/knotis/run/eggs 2> /dev/null
virtualenv /srv/knotis/venv

${installer_dir}/install_all.sh

# clean up temp directory
rm -r /tmp/knotis

# create users
useradd --system --no-create-home --home-dir /srv/knotis/ --user-group knotis
chsh -s /bin/bash knotis
chown -R knotis:knotis /srv/knotis