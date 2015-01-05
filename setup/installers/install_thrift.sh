#!/bin/bash
echo 'installing thrift ...'
pip="${install_location}/venv/bin/pip"
${pip} install thrift

rand=$(date | md5sum)
rand=(${rand})
temp_dir="${tmp}/${rand[0]}"
thrift_tarball=${setup_dir}/static/thrift-0.9.1.tar.gz
mkdir ${temp_dir}
tar xvf ${thrift_tarball} -C ${temp_dir}
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
thrift -gen py ${CASSANDRA_THRIFT_INTERFACE}
cp -af ./gen-py/cassandra ${install_location}/venv/lib/python2.7/site-packages/
rm -rf ./gen-py
rm -rf ${temp_dir}
