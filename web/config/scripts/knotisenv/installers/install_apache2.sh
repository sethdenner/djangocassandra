#!/bin/bash
if [[ -z ${apache2_config} ]] ; then
    if [[ $# -gt 0 ]] ; then
        apache2_config="${1}"

    else
        echo "error installing apache2. no configuration file specified."
        exit 1

    fi

fi

if [[ -z ${modwsgi_script} ]] ; then
    if [[ $# -eq 2 ]] ; then
        modwsgi_script="${2}"

    else
        echo "error installing apache2. no modwsgi script specified."
        exit 1

    fi

fi

my_dir="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. ${my_dir}/../../utilities/quick_install.sh

apt-get -y install apache2-mpm-worker apache2-dev

modwsgi_tarball='http://modwsgi.googlecode.com/files/mod_wsgi-3.4.tar.gz'
quick_install wget ${modwsgi_tarball} make

echo "LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so" > /etc/apache2/mods-available/wsgi.load
a2enmod wsgi
mkdir -p /srv/knotis/app/conf/apache
mkdir -p /srv/knotis/app/media

cp ${modwsgi_script} /srv/knotis/app/conf/apache/
cp ${apache2_config} /etc/apache2/sites-available/

a2dissite default
a2ensite seth.knotis.com

service apache2 restart
