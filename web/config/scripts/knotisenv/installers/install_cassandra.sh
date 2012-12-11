#!/bin/bash
my_dir="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# setup cassandra source
apt_sources=/etc/apt/sources.list
cassandra_deb='deb http://www.apache.org/dist/cassandra/debian 10x main'
cassandra_deb_src='deb-src http://www.apache.org/dist/cassandra/debian 10x main'
grep "$cassandra_deb" ${apt_sources} -q || echo ${cassandra_deb} >> ${apt_sources}
grep "$cassandra_deb_src" ${apt_sources} -q || echo ${cassandra_deb_src} >> ${apt_sources}

gpg --keyserver pgp.mit.edu --recv-keys F758CE318D77295D
gpg --export --armor F758CE318D77295D | sudo apt-key add -

gpg --keyserver pgp.mit.edu --recv-keys 2B5C1B00
gpg --export --armor 2B5C1B00 | sudo apt-key add -

apt-get update
apt-get install cassandra

cp -f /etc/cassandra/cassandra.yaml /etc/cassandra/cassandra.yaml.backup
cp -f ${my_dir}../configuration/cassandra/cassandra.yaml /etc/cassandra/cassandra.yaml
