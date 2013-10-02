#!/bin/bash

apt-get install -y python-virtualenv virtualenvwrapper python-pip

virtualenv ${install_location}/venv || { echo "Failed to create knotis virtual environment at ${install_location}/venv" >&2 ; exit 1 ; }
