#!/bin/bash

if [[ ! -d ${1} ]] ; then
    echo "ERROR: Directory ${1} does not exist."
    return 1

fi

(
    cd "$(dirname "$0")"
    ./maintenance_mode.sh enable
    ./site_copy.sh ${1}
    ./site_refresh.sh
    ./maintenance_mode.sh disable
)

chown -R knotis:knotis /srv/knotis
