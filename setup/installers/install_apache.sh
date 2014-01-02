#!/bin/bash
set -e
my_dir="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

apt-get -y install apache2-mpm-worker apache2-dev

rand=$(date | md5sum)
rand=(${rand})
temp_dir="${tmp}/${rand[0]}"
modwsgi_tarball="${setup_dir}/static/mod_wsgi-3.4.tar.gz"

rm -rf ${temp_dir} 2> /dev/null
mkdir -p ${temp_dir}
tar xvf ${modwsgi_tarball} -C ${temp_dir}
(
    cd ${temp_dir}
    bootstrap_script=$(find . -maxdepth 2 -name bootstrap.sh)
    if [[ ${bootstrap_script} ]] ; then
        (
            cd ${bootstrap_script%/*}
            ./${bootstrap_script##*/}
            
        )
    fi
    configure_script=$(find . -maxdepth 2 -name configure)
    if [[ ${configure_script} ]] ; then
        (
            cd ${configure_script%/*}
            ./${configure_script##*/}
            make
            make install
        )
    fi
)

echo "LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so" > /etc/apache2/mods-available/wsgi.load
a2enmod wsgi
mkdir -p ${install_location}/app/conf/apache
mkdir -p ${install_location}/app/media

cp ${MODWSGI_SCRIPT} /srv/knotis/app/conf/apache/
cp ${APACHE2_CONFIG} /etc/apache2/sites-available/

a2dissite default
a2ensite $(basename ${APACHE2_CONFIG})

service apache2 restart
