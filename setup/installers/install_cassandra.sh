#!/bin/bash
dpkg -i $(readlink -e "${setup_dir}/static/cassandra_2.0.0_all.deb")

service cassandra stop

rm -rf /var/lib/cassandra/*
cp ${CASSANDRA_CONFIG} /etc/cassandra/cassandra.yaml
cp ${CASSANDRA_ENV} /etc/cassandra/cassandra-env.sh

service cassandra start
