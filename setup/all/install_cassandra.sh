#!/bin/bash

my_dir="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
dpkg -i $(readlink -m "${my_dir}/static/cassandra_2.0.0_all.deb")