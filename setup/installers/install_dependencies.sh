#!/bin/bash

apt-get install -y libboost-dev libboost-test-dev libboost-program-options-dev libevent-dev libtool flex bison pkg-config g++ libssl-dev python python-dev python-setuptools python-software-properties python-support python-twisted mercurial make automake autoconf acl gcc git mercurial libmysqlclient-dev || { echo 'Failed to install dependencies' >&2 ; exit 1 ; }
