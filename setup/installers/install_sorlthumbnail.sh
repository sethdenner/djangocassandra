#!/bin/bash
echo 'installing sorl-thumbnail ...'
sorlthumbnail_git=git+https://github.com/simlay/sorl-thumbnail.git@fix_cropping_django_1.3

${install_location}/venv/bin/pip install git+${sorlthumbnail_git}
