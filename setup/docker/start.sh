#!/bin/bash

chmod -R o+rw ${install_location}

service apache2 start & disown

tail -f /var/log/apache2/access.log
