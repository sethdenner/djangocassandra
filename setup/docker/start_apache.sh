#!/bin/sh

chown -R ${ADMIN_USER}:${ADMIN_GROUP} ${install_location}

chmod -R u+rw ${install_location}
service apache2 start
