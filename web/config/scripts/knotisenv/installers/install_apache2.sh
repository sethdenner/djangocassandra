#!/bin/bash
my_dir="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. ${my_dir}/../../utilities/quick_install.sh

apt-get -y install apache2-mpm-worker apache2-dev

modwsgi_tarball='http://modwsgi.googlecode.com/files/mod_wsgi-3.4.tar.gz'
quick_install wget ${modwsgi_tarball} make

echo "LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so" > /etc/apache2/mods-available/wsgi.load
a2enmod wsgi
mkdir -p /srv/knotis/app/conf/apache

mkdir -p /srv/knotis/app/media
cd /srv/knotis/app/conf/apache/
cp ${my_dir}/../configuration/modwsgi/knotis.wsgi /srv/knotis/app/conf/apache/knotis.wsgi
cp ${my_dir}/../configuration/apache2/seth.knotis.com /etc/apache2/sites-available/seth.knotis.com

a2dissite default
a2ensite seth.knotis.com

service apache2 restart
