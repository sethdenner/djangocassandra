#!/bin/bash

./maintenance_mode enable
./site_copy.sh $(./download_knotis.sh)
./site_refresh.sh
./maintenance_mode disable