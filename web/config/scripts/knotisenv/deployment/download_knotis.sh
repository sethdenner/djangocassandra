#!/bin/bash

download_uri=git@bitbucket.org:knotiscom/knotis.com.git
if [[ "$#" -gt 0 ]] ; then
    download_uri=${1}

fi

git clone download_uri
echo "$(pwd)/knotis.com"
