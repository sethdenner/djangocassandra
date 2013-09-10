#!/bin/bash
set -e

apache2_config=$(readlink -m "${env_dir}/config/apache2/${APACHE2_CONFIG}")
if [[ ! -f ${apache2_config} ]] ; then
    apache2_config=$(readlink -m "${all_dir}/config/apache2/${APACHE2_CONFIG}")
fi
if [[ ! -f ${apache2_config} ]] ; then
    echo "There is no apache2 config available for environment ${ENVIRONMENT_NAME}" >&2 ; exit 1 ;
fi

modwsgi_script=$(readlink -m "${env_dir}/config/modwsgi/${MODWSGI_SCRIPT}")
if [[ ! -f ${modwsgi_script} ]] ; then
    modwsgi_script=$(readlink -m "${all_dir}/config/modwsgi/${MODWSGI_SCRIPT}")
fi
if [[ ! -f ${modwsgi_script} ]] ; then
    echo "There is no modwsgi script available for environment ${env_name}" >&2 ; exit 1 ;
fi

apt-get -y install apache2-mpm-worker apache2-dev

rand=$(date | md5sum)
rand=(${rand})
temp_dir="./tmp/${rand[0]}"
my_dir="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
modwsgi_tarball="${my_dir}/static/mod_wsgi-3.4.tar.gz"

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

cp ${modwsgi_script} /srv/knotis/app/conf/apache/
cp ${apache2_config} /etc/apache2/sites-available/

a2dissite default
a2ensite $(basename ${APACHE2_CONFIG})

service apache2 restart
