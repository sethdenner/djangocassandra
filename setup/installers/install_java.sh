#!/bin/bash

add-apt-repository -y ppa:webupd8team/java || { echo 'Failed to add repository ppa:webupd8team/java' >&2; exit 1; }
apt-get update

apt-get install -y jsvc libcap2 libcommons-daemon-java libjna-java || { echo 'Failed to install java dependencies.' >&2; exit 1; }


# Make java install silently. 
echo debconf shared/accepted-oracle-license-v1-1 select true | debconf-set-selections
echo debconf shared/accepted-oracle-license-v1-1 seen true | debconf-set-selections

apt-get install -y oracle-java7-installer
