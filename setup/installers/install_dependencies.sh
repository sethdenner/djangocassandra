#!/bin/bash

apt-get install -y libboost-dev libboost-test-dev libboost-program-options-dev libevent-dev libtool flex bison pkg-config g++ libssl-dev python python-dev python-setuptools python-software-properties python-support python-twisted mercurial make automake autoconf acl gcc git libmysqlclient-dev python-pip libjpeg8 libjpeg-dev libfreetype6 libfreetype6-dev zlib1g-dev python-virtualenv || { echo 'Failed to install dependencies' >&2 ; exit 1 ; }

