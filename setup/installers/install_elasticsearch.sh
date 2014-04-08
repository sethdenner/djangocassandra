#!/bin/bash

venv_bin=/srv/knotis/venv/bin

echo 'installing elasticsearch ...'

#cd 
#apt-get update
#apt-get install openjdk-7-jre-headless -y
 
 
### Check http://www.elasticsearch.org/download/ for latest version of ElasticSearch and replace wget link below
 
# NEW WAY / EASY WAY
wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-0.90.4.deb
sudo dpkg -i elasticsearch-0.90.4.deb
sudo service elasticsearch start

$venv_bin/pip install 'pyelasticsearch'
