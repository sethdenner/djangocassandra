#!/bin/bash

apt-get install -y git python-software-properties python-support python-dev make || { echo 'Failed to install dependencies' >&2 ; exit 1 ; }
