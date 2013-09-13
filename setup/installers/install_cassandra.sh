#!/bin/bash
dpkg -i $(readlink -e "${setup_dir}/static/cassandra_2.0.0_all.deb")

service cassandra stop

cp ${CASSANDRA_CONFIG} /etc/cassandra/cassandra.yaml

service cassandra start
