#!/bin/bash

if [[ -d "/srv/knotis/app/prev" ]] ; then
    rm -rf /srv/knotis/app/web
    mv -rf /srv/knotis/app/prev /srv/knotis/app/web

fi
