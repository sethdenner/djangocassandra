#!/bin/bash
my_dir="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. ${my_dir}/../../utilities/quick_install.sh

apt-get install -y libboost-dev libboost-test-dev libboost-program-options-dev libevent-dev automake libtool flex bison pkg-config g++ libssl-dev python-dev python-twisted openjdk-6-jdk

venv_bin=/srv/knotis/venv/bin

echo 'installing thrift ...'
$venv_bin/pip install thrift

thrift_tarball=https://dist.apache.org/repos/dist/release/thrift/0.9.0/thrift-0.9.0.tar.gz
quick_install wget ${thrift_tarball} make

# download and build cassandra thrift interface

rand=$(date | md5sum)
rand=(${rand})
temp_dir="./cassandra-${rand[0]}"
cassandra_tarball=apache-cassandra-1.1.7-bin.tar.gz
cassandra_tarball_uri=http://apache.tradebit.com/pub/cassandra/1.1.7/${cassandra_tarball}
wget ${cassandra_tarball_uri} -P ${temp_dir}
(
    cd ${temp_dir}
    tar xvf ${cassandra_tarball}
    cassandra_thrift="$(find . -name cassandra.thrift)"
    thrift -gen py ${cassandra_thrift}
    cp -rf ./gen-py/cassandra /srv/knotis/venv/lib/python2.7/site-packages/
)
rm -rf ${temp_dir}

