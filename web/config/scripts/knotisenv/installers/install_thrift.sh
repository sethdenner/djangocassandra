#!/bin/bash
my_dir="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. ${my_dir}/../../utilities/quick_install.sh

apt-get install -y libboost-dev libboost-test-dev libboost-program-options-dev libevent-dev automake libtool flex bison pkg-config g++ libssl-dev python-dev python-twisted openjdk-6-jdk

venv_bin=/srv/knotis/venv/bin

echo 'installing thrift ...'
$venv_bin/pip install thrift

thrift_tarball=https://dist.apache.org/repos/dist/release/thrift/0.9.0/thrift-0.9.0.tar.gz
quick_install wget ${thrift_tarball} make
