#!/bin/bash

if [[ ! -d ${1} ]] ; then
    echo "ERROR: Directory ${1} does not exist."
    return 1

fi

./maintenance_mode enable
./site_copy.sh ${1}
./site_refresh.sh
./maintenance_mode disable
